"""
diagnose_csv.py

Run this to see exactly what your CSV looks like so we can fix the loader.

Usage:
    python diagnose_csv.py --dataset dataset/PGEquiCite_Dataset.csv
"""

import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", required=True)
args = parser.parse_args()

print(f"Reading: {args.dataset}\n")

# Check raw bytes at start of file
with open(args.dataset, "rb") as f:
    raw = f.read(200)
print("=== First 200 raw bytes ===")
print(repr(raw))
print()

# Try reading as text and show first 5 rows
for encoding in ("utf-8-sig", "utf-8", "latin-1"):
    try:
        with open(args.dataset, newline="", encoding=encoding) as f:
            reader = csv.reader(f)
            rows = [next(reader) for _ in range(6) if True]
        print(f"=== First 6 rows (encoding={encoding}) ===")
        for i, row in enumerate(rows):
            print(f"  Row {i}: {row[:4]}")  # show first 4 columns only
        print()
        break
    except Exception as e:
        print(f"  Failed with {encoding}: {e}")

# Try DictReader and show what item_id column contains
print("=== item_id column (first 10 non-blank values) ===")
for encoding in ("utf-8-sig", "utf-8", "latin-1"):
    try:
        with open(args.dataset, newline="", encoding=encoding) as f:
            reader = csv.DictReader(f)
            print(f"  Headers: {list(reader.fieldnames)[:6]}")
            count = 0
            for row in reader:
                # Try common variants of the column name
                for key in ["item_id", "item_id ", " item_id", "Item_id", "Item ID"]:
                    val = row.get(key, "")
                    if val:
                        print(f"  item_id={repr(val)}")
                        count += 1
                        break
                if count >= 10:
                    break
        break
    except Exception as e:
        print(f"  Failed with {encoding}: {e}")