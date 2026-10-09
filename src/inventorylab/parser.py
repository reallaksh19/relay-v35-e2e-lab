"""Feature A contract: strict CSV ingestion. Intentionally NOT IMPLEMENTED."""
from decimal import Decimal
from typing import NamedTuple


class InventoryRow(NamedTuple):
    sku: str
    quantity: int
    unit_price: Decimal


def parse_inventory_csv(text: str) -> list[InventoryRow]:
    """Parse CSV with required columns sku, quantity, unit_price; fail closed on invalid data."""
    raise NotImplementedError("LAB-R1 intentionally RED: implement in parser PR")
