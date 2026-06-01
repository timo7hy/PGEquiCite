# dev/dataset.py
"""
Loads the PGEquiCite dataset from CSV.
Returns a list of BenchmarkItem objects, each containing one query and
its full abstract pool ready to pass to a model.

Expected CSV columns (order must match COL map below):
    item_id, abstract_id, pmid, title, authors, year, journal,
    abstract_text, population_label, affiliation_label,
    annotator_1_pop, annotator_2_pop, annotator_1_aff, annotator_2_aff,
    query, equity_gap_severity, reference_answer

Note: must_cite_abstracts column has been removed. Coverage is now computed
from population group breadth across all abstracts in the pool — see scorer.py.
"""

from dataclasses import dataclass, field
from pathlib import Path
import csv


# ── Column index map (1-based, matching CSV column order) ────────────────────
COL = {
    "item_id":              1,
    "abstract_id":          2,
    "pmid":                 3,
    "title":                4,
    "authors":              5,
    "year":                 6,
    "journal":              7,
    "abstract_text":        8,
    "population_label":     9,
    "affiliation_label":   10,
    "annotator_1_pop":     11,
    "annotator_2_pop":     12,
    "annotator_1_aff":     13,
    "annotator_2_aff":     14,
    "query":               15,
    "equity_gap_severity": 16,
    "reference_answer":    17,
}


@dataclass
class Abstract:
    abstract_id:       str
    pmid:              str
    title:             str
    authors:           str
    year:              str
    journal:           str
    abstract_text:     str
    population_label:  str
    affiliation_label: str


@dataclass
class BenchmarkItem:
    item_id:             str
    gene_drug_pair:      str
    query:               str
    equity_gap_severity: str
    reference_answer:    str
    abstracts:           list[Abstract] = field(default_factory=list)

    @property
    def pool_text(self) -> str:
        """Format abstract pool for insertion into the model prompt."""
        lines = []
        for i, ab in enumerate(self.abstracts, start=1):
            lines.append(
                f"[{i}] {ab.title}\n"
                f"{ab.authors} ({ab.year}) — {ab.journal}\n"
                f"Abstract: {ab.abstract_text}\n"
            )
        return "\n".join(lines)


# Gene code → human-readable gene-drug pair name
_GENE_DRUG_MAP = {
    "N": "NUDT15 / Thiopurines",
    "C": "CYP2C19 / Clopidogrel",
    "G": "G6PD / Primaquine",
    "S": "SLCO1B1 / Statins",
    "H": "HLA-B*57:01 / Abacavir",
    "D": "CYP2D6 / Codeine",
}

def _infer_gene_drug(item_id: str) -> str:
    parts = item_id.split("-")
    if len(parts) >= 2:
        return _GENE_DRUG_MAP.get(parts[1].upper(), f"Unknown ({parts[1]})")
    return "Unknown"


def load_dataset(csv_path: str | Path) -> list[BenchmarkItem]:
    """
    Load benchmark items from the PGEquiCite CSV dataset.

    Args:
        csv_path: Path to PGEquiCite_Dataset.csv

    Returns:
        List of BenchmarkItem objects, one per unique item_id,
        each with all 10 abstracts attached.
    """
    items: dict[str, BenchmarkItem] = {}

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        # Normalise header names — strip whitespace
        raw_headers = reader.fieldnames or []
        header_map = {h.strip(): h for h in raw_headers}

        def get(row, key):
            actual = header_map.get(key, key)
            return str(row.get(actual, "") or "").strip()

        for row in reader:
            item_id = get(row, "item_id")
            if not item_id or not item_id.startswith("PGEQUICITE"):
                continue

            abstract = Abstract(
                abstract_id      = get(row, "abstract_id"),
                pmid             = get(row, "pmid"),
                title            = get(row, "title"),
                authors          = get(row, "authors"),
                year             = get(row, "year"),
                journal          = get(row, "journal"),
                abstract_text    = get(row, "abstract_text"),
                population_label = get(row, "population_label"),
                affiliation_label= get(row, "affiliation_label"),
            )

            if item_id not in items:
                items[item_id] = BenchmarkItem(
                    item_id             = item_id,
                    gene_drug_pair      = _infer_gene_drug(item_id),
                    query               = get(row, "query"),
                    equity_gap_severity = get(row, "equity_gap_severity"),
                    reference_answer    = get(row, "reference_answer"),
                )

            items[item_id].abstracts.append(abstract)

    return list(items.values())
