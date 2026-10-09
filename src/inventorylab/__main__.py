"""Lab CLI: real entrypoint, feature work remains in separate PRs."""
import argparse
import json
from pathlib import Path
from .parser import parse_inventory_csv
from .report import inventory_report


def main() -> int:
    ap = argparse.ArgumentParser(description="Inventory CSV to JSON (lab prototype)")
    ap.add_argument("csv_file", type=Path)
    args = ap.parse_args()
    rows = parse_inventory_csv(args.csv_file.read_text(encoding="utf-8"))
    print(json.dumps(inventory_report(rows), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
