"""Feature B contract: deterministic inventory JSON. Intentionally NOT IMPLEMENTED."""
from .parser import InventoryRow


def inventory_report(rows: list[InventoryRow]) -> dict:
    """Return item values and total as exact decimal strings with stable SKU sorting."""
    raise NotImplementedError("LAB-R2 intentionally RED: implement in report PR")
