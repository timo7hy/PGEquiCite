"""
generate_prompts.py

Reads PGEquiCite_Dataset.csv and prints every evaluation prompt
formatted for manual copy-paste into ChatGPT, Claude, or Gemini.

Usage:
    python generate_prompts.py --dataset PGEquiCite_Dataset.csv

Outputs a single text file: prompts_for_review.txt
Each prompt is clearly labelled and separated so you can
copy-paste one at a time into any LLM interface.

Conditions generated per item:
    - pool     : model receives query + all abstracts
    - baseline : model receives query only (no abstracts)
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

# ── Prompt templates (same as eval pipeline) ─────────────────────────────────

POOL_TEMPLATE = """\
You are a pharmacogenomics research assistant.

Using ONLY the abstracts provided below, write a comprehensive summary of \
the current evidence on the following question. Cite each paper you use by \
last name of first author and year in parentheses, e.g. (Yang et al., 2014). \
Do not use any knowledge outside of the abstracts provided.

QUESTION:
{query}

ABSTRACTS:
{pool_text}"""

BASELINE_TEMPLATE = """\
You are a pharmacogenomics research assistant.

Write a comprehensive summary of the current pharmacogenomic evidence on \
the following question. Cite specific papers by last name of first author \
and year in parentheses, e.g. (Yang et al., 2014).

QUESTION:
{query}"""

DIVIDER = "=" * 80


# ── CSV loader ────────────────────────────────────────────────────────────────

def load_csv(path: Path) -> dict[str, dict]:
    """
    Load the MASTER CSV into a dict keyed by item_id.
    Each value has:
        query       : str
        abstracts   : list of dicts with keys title, authors, year, journal, abstract_text
    """
    items: dict[str, dict] = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Normalise header names (strip whitespace, lowercase for lookup)
        raw_headers = reader.fieldnames or []
        header_map = {h.strip(): h for h in raw_headers}

        def get(row, key):
            actual = header_map.get(key, key)
            return str(row.get(actual, "") or "").strip()

        for row in reader:
            item_id = get(row, "item_id")

            # Skip blank or non-item rows
            if not item_id or not item_id.startswith("PGEQUICITE"):
                continue

            query = get(row, "query")

            abstract = {
                "abstract_id":   get(row, "abstract_id"),
                "title":         get(row, "title"),
                "authors":       get(row, "authors"),
                "year":          get(row, "year"),
                "journal":       get(row, "journal"),
                "abstract_text": get(row, "abstract_text"),
            }

            if item_id not in items:
                items[item_id] = {"query": query, "abstracts": []}

            items[item_id]["abstracts"].append(abstract)

    return items


# ── Pool text builder ─────────────────────────────────────────────────────────

def build_pool_text(abstracts: list[dict]) -> str:
    lines = []
    for i, ab in enumerate(abstracts, start=1):
        lines.append(
            f"[{i}] {ab['title']}\n"
            f"{ab['authors']} ({ab['year']}) — {ab['journal']}\n"
            f"Abstract: {ab['abstract_text']}"
        )
    return "\n\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate PGEquiCite prompts for manual evaluation")
    parser.add_argument("--dataset", required=True, help="Path to PGEquiCite_Dataset.csv")
    parser.add_argument("--conditions", default="pool,baseline",
                        help="Conditions to generate: pool,baseline (default: both)")
    parser.add_argument("--items", default="all",
                        help="Comma-separated item IDs or 'all' (default: all)")
    parser.add_argument("--output", default="prompts_for_review.txt",
                        help="Output file name (default: prompts_for_review.txt)")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"ERROR: File not found: {dataset_path}")
        sys.exit(1)

    conditions = [c.strip() for c in args.conditions.split(",")]
    item_filter = (
        None if args.items == "all"
        else {i.strip() for i in args.items.split(",")}
    )

    print(f"Loading dataset from {dataset_path}...")
    items = load_csv(dataset_path)

    if item_filter:
        items = {k: v for k, v in items.items() if k in item_filter}

    if not items:
        print("ERROR: No items loaded. Check that MASTER tab rows start with PGEQUICITE.")
        sys.exit(1)

    print(f"Loaded {len(items)} item(s): {', '.join(sorted(items.keys()))}")

    output_lines = []

    # Header block
    output_lines.append(DIVIDER)
    output_lines.append("PGEquiCite — Manual Evaluation Prompts")
    output_lines.append(f"Dataset: {dataset_path.name}")
    output_lines.append(f"Items: {len(items)}  |  Conditions: {conditions}")
    output_lines.append(f"Total prompts: {len(items) * len(conditions)}")
    output_lines.append(DIVIDER)
    output_lines.append("")
    output_lines.append("HOW TO USE THIS FILE")
    output_lines.append("-" * 40)
    output_lines.append("1. Open ChatGPT, Claude, or Gemini in a FRESH conversation")
    output_lines.append("2. Copy everything between the START and END markers for one prompt")
    output_lines.append("3. Paste into the LLM and submit")
    output_lines.append("4. Copy the full response into your results spreadsheet")
    output_lines.append("5. Record which ITEM ID and CONDITION you ran")
    output_lines.append("6. Start a NEW conversation for each prompt (no shared context)")
    output_lines.append("")

    # Results tracking table
    output_lines.append("RESULTS TRACKING TABLE — fill this in as you go")
    output_lines.append("-" * 40)
    header = f"{'Prompt #':<10} {'Item ID':<22} {'Condition':<10} {'Model':<20} {'Done?'}"
    output_lines.append(header)
    output_lines.append("-" * len(header))

    prompt_num = 0
    for item_id in sorted(items.keys()):
        for condition in conditions:
            prompt_num += 1
            output_lines.append(
                f"{prompt_num:<10} {item_id:<22} {condition:<10} {'':20} {'[ ]'}"
            )

    output_lines.append("")
    output_lines.append(DIVIDER)
    output_lines.append("")

    # Generate each prompt
    prompt_num = 0
    for item_id in sorted(items.keys()):
        item = items[item_id]
        query = item["query"]
        abstracts = item["abstracts"]
        pool_text = build_pool_text(abstracts)

        for condition in conditions:
            prompt_num += 1

            if condition == "pool":
                prompt_text = POOL_TEMPLATE.format(query=query, pool_text=pool_text)
            elif condition == "baseline":
                prompt_text = BASELINE_TEMPLATE.format(query=query)
            else:
                continue

            # Prompt header
            output_lines.append(f"PROMPT #{prompt_num}")
            output_lines.append(f"Item ID:   {item_id}")
            output_lines.append(f"Condition: {condition.upper()}")
            if condition == "pool":
                output_lines.append(f"Abstracts: {len(abstracts)} provided to model")
            else:
                output_lines.append("Abstracts: NONE — tests model pretraining only")
            output_lines.append(f"Query:     {query[:100]}{'...' if len(query) > 100 else ''}")
            output_lines.append("")
            output_lines.append(">>> COPY EVERYTHING BELOW THIS LINE >>>")
            output_lines.append("-" * 40)
            output_lines.append(prompt_text)
            output_lines.append("-" * 40)
            output_lines.append("<<< END OF PROMPT <<<")
            output_lines.append("")
            output_lines.append(DIVIDER)
            output_lines.append("")

    # Write output file
    output_path = Path(args.output)
    output_path.write_text("\n".join(output_lines), encoding="utf-8")

    print(f"\nDone. {prompt_num} prompts written to: {output_path}")
    print("\nQuick summary:")
    for item_id in sorted(items.keys()):
        ab_count = len(items[item_id]["abstracts"])
        print(f"  {item_id}: {ab_count} abstracts, {len(conditions)} prompt(s)")


if __name__ == "__main__":
    main()