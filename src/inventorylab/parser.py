"""Feature A contract: strict CSV ingestion."""
import csv
from decimal import Decimal
import io
from typing import NamedTuple


class InventoryRow(NamedTuple):
    sku: str
    quantity: int
    unit_price: Decimal


def parse_inventory_csv(text: str) -> list[InventoryRow]:
    """Parse CSV with required columns sku, quantity, unit_price; fail closed on invalid data."""
    if not text or not text.strip():
        raise ValueError("Empty CSV input")

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        raise ValueError("Missing header row")

    if header != ["sku", "quantity", "unit_price"]:
        raise ValueError(f"Invalid headers: expected ['sku', 'quantity', 'unit_price'], got {header}")

    rows: list[InventoryRow] = []
    for row in reader:
        if not row:
            continue
        if len(row) != 3:
            raise ValueError(f"Malformed row: expected 3 columns, got {len(row)}")
        sku = row[0]
        qty = int(row[1])
        price = Decimal(row[2])
        rows.append(InventoryRow(sku, qty, price))
    return rows
