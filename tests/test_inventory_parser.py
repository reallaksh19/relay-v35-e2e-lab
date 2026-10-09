import unittest
from decimal import Decimal
from inventorylab.parser import parse_inventory_csv, InventoryRow


class ParserContract(unittest.TestCase):
    def test_valid_rows_preserve_source_order_and_decimal_precision(self):
        text = "sku,quantity,unit_price\nB,2,3.10\nA,1,0.20\n"
        self.assertEqual(parse_inventory_csv(text), [
            InventoryRow("B", 2, Decimal("3.10")), InventoryRow("A", 1, Decimal("0.20")),
        ])

    def test_duplicate_sku_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_inventory_csv("sku,quantity,unit_price\nA,1,1.00\nA,2,1.00\n")

    def test_negative_quantity_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_inventory_csv("sku,quantity,unit_price\nA,-1,1.00\n")

    def test_bad_headers_and_nonfinite_price_fail_closed(self):
        for text in ("sku,quantity\nA,2\n", "sku,quantity,unit_price\nA,1,NaN\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_inventory_csv(text)
