# dev/run_eval.py
"""
Main evaluation runner for PGEquiCite.

Usage:
    python run_eval.py --dataset ../dataset/PGEquiCite_Dataset.csv

Options:
    --dataset       Path to PGEquiCite_Dataset.csv (required)
    --conditions    pool,baseline (default: both)
    --models        anthropic,openai,google or 'all' (default: all)
    --items         Comma-separated item IDs or 'all' (default: all)
    --dry-run       Print prompts without calling any API
    --output-dir    Directory for result files (default: ./results)
    --delay         Seconds between API calls (default: 2)
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

from dataset import load_dataset
from prompt import build_pool_prompt, build_baseline_prompt
from scorer import score_response
from results import write_csv_results, write_review_workbook, RESULTS_DIR
from models import ALL_CLIENTS


def parse_args():
    p = argparse.ArgumentParser(description="PGEquiCite evaluation runner")
    p.add_argument("--dataset",    required=True)
    p.add_argument("--conditions", default="pool,baseline")
    p.add_argument("--models",     default="all")
    p.add_argument("--items",      default="all")
    p.add_argument("--dry-run",    action="store_true")
    p.add_argument("--output-dir", default="results")
    p.add_argument("--delay",      type=float, default=2.0)
    return p.parse_args()


def build_clients(model_filter: str) -> list:
    clients = []
    for ClientClass in ALL_CLIENTS:
        if model_filter != "all":
            requested = {m.strip().lower() for m in model_filter.split(",")}
            if ClientClass.provider not in requested:
                continue
        try:
            client = ClientClass()
            clients.append(client)
            print(f"  ✓ Loaded {client}")
        except EnvironmentError as e:
            print(f"  ✗ Skipping {ClientClass.__name__}: {e}")
    return clients


def main():
    args = parse_args()
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found: {dataset_path}")
        sys.exit(1)

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    conditions = [c.strip() for c in args.conditions.split(",")]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n── PGEquiCite Evaluation Runner ─────────────────────────────")
    print(f"  Dataset:    {dataset_path}")
    print(f"  Conditions: {conditions}")
    print(f"  Dry run:    {args.dry_run}")

    print("\n── Loading dataset...")
    items = load_dataset(dataset_path)
    if args.items != "all":
        requested = {i.strip() for i in args.items.split(",")}
        items = [it for it in items if it.item_id in requested]
    print(f"  {len(items)} item(s) loaded.")
    for it in items:
        from scorer import classify_abstract
        from collections import Counter
        groups = Counter(
            classify_abstract(ab.population_label, ab.affiliation_label)
            for ab in it.abstracts
        )
        print(f"    {it.item_id} — {it.gene_drug_pair} | groups: {dict(groups)}")

    print("\n── Initialising model clients...")
    if args.dry_run:
        print("  DRY RUN — no API calls.")
        clients = []
    else:
        clients = build_clients(args.models)
        if not clients:
            print("  ERROR: No clients initialised. Check API keys.")
            sys.exit(1)

    all_results = []
    total_calls = len(items) * len(conditions) * (len(clients) or 1)
    call_num = 0

    print(f"\n── Running evaluations ({total_calls} calls)...")

    for item in items:
        for condition in conditions:
            prompt = (
                build_pool_prompt(item.query, item.pool_text)
                if condition == "pool"
                else build_baseline_prompt(item.query)
            )

            if args.dry_run:
                call_num += 1
                print(f"\n[{call_num}] DRY RUN — {item.item_id} / {condition}")
                print("  " + prompt[:400].replace("\n", "\n  ") + "...")
                continue

            for client in clients:
                call_num += 1
                print(f"  [{call_num}/{total_calls}] {item.item_id} / {condition} / {client.model_id} ...",
                      end=" ", flush=True)

                response = client.generate(prompt)

                if response.error:
                    print(f"ERROR: {response.error}")
                else:
                    print(f"OK ({len(response.response_text)} chars)")

                result = score_response(item, response, condition)
                all_results.append(result)

                print(f"       Coverage: {result.covered_groups} → {result.coverage_score}/3 "
                      f"| missed: {result.missed_groups}")

                if args.delay > 0:
                    time.sleep(args.delay)

    if all_results:
        print(f"\n── Writing results ({len(all_results)} rows)...")
        scores_path, responses_path = write_csv_results(all_results, ts)
        review_path = write_review_workbook(all_results, ts)
        print(f"  Scores:          {scores_path}")
        print(f"  Responses:       {responses_path}")
        print(f"  Review workbook: {review_path}")

        print("\n── Coverage summary ─────────────────────────────────────────")
        from collections import defaultdict
        groups: dict = defaultdict(list)
        for r in all_results:
            groups[(r.model_id, r.condition)].append(r.coverage_score)
        header = f"{'Model':<30} {'Condition':<10} {'Avg Coverage':>12} {'Items':>6}"
        print(header)
        print("-" * len(header))
        for (model, cond), scores in sorted(groups.items()):
            print(f"{model:<30} {cond:<10} {sum(scores)/len(scores):>12.2f} {len(scores):>6}")

    print("\nDone.")


if __name__ == "__main__":
    main()
