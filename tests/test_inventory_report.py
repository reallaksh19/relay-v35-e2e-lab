import unittest
from decimal import Decimal
from inventorylab.parser import InventoryRow
from inventorylab.report import inventory_report


class ReportContract(unittest.TestCase):
    def test_deterministic_sku_sort_and_money(self):
        rows = [InventoryRow("Z", 2, Decimal("3.10")), InventoryRow("A", 3, Decimal("0.20"))]
        self.assertEqual(inventory_report(rows), {
            "items": [
                {"sku": "A", "quantity": 3, "unit_price": "0.20", "value": "0.60"},
                {"sku": "Z", "quantity": 2, "unit_price": "3.10", "value": "6.20"},
            ], "total": "6.80",
        })

    def test_empty_is_zero(self):
        self.assertEqual(inventory_report([]), {"items": [], "total": "0.00"})
