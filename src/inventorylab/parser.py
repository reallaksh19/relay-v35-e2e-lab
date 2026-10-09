"""Feature A contract: strict CSV ingestion. Replaces initial NotImplementedError stub."""
import csv
from decimal import Decimal, InvalidOperation
import io
from typing import NamedTuple


class InventoryRow(NamedTuple):
    sku: str
    quantity: int
    unit_price: Decimal


EXPECTED_HEADERS = ("sku", "quantity", "unit_price")


def parse_inventory_csv(text: str) -> list[InventoryRow]:
    """Parse CSV with required columns sku, quantity, unit_price; fail closed on invalid data."""
    if not text or not text.strip():
        raise ValueError("Empty or whitespace-only CSV input")

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        raise ValueError("Missing header row")

    if tuple(header) != EXPECTED_HEADERS:
        raise ValueError(f"Invalid headers: expected {list(EXPECTED_HEADERS)}, got {header}")

    rows: list[InventoryRow] = []
    seen_skus: set[str] = set()

    for line_num, row in enumerate(reader, start=2):
        if not row:
            continue
        if len(row) != 3:
            raise ValueError(f"Line {line_num}: expected 3 columns, got {len(row)}")

        sku, qty_str, price_str = row[0], row[1], row[2]

        if not sku or not sku.strip():
            raise ValueError(f"Line {line_num}: blank or whitespace SKU")
        if sku in seen_skus:
            raise ValueError(f"Line {line_num}: duplicate SKU '{sku}'")
        seen_skus.add(sku)

        try:
            qty = int(qty_str)
        except (ValueError, TypeError):
            raise ValueError(f"Line {line_num}: invalid integer quantity '{qty_str}'")
        if qty < 0:
            raise ValueError(f"Line {line_num}: negative quantity {qty}")

        try:
            price = Decimal(price_str)
        except (InvalidOperation, TypeError):
            raise ValueError(f"Line {line_num}: invalid decimal unit price '{price_str}'")
        if not price.is_finite():
            raise ValueError(f"Line {line_num}: non-finite unit price '{price_str}'")
        if price < Decimal("0"):
            raise ValueError(f"Line {line_num}: negative unit price '{price_str}'")

        rows.append(InventoryRow(sku, qty, price))

    return rows
