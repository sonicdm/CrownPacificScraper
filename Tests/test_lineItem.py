from unittest import TestCase

from crownpacific.product import Product
from crownpacific.purchase_order import LineItem


class TestLineItem(TestCase):
    
    def setUp(self):
        self.test_product = Product()
        self.test_product.brand = "Test"
        self.test_product.upc = "123456-12345"
        self.test_product.case_cost = "$12.34"
        self.test_product.each_cost = "$1.23"
        self.test_product.item = 123456
        self.test_product.srp = "2.34"
        self.test_product.attributes = "Test Attribute 1, Test Attribute 2"

    def test_line_item_constructor(self):

        line_item = LineItem(123456, 1, "$123.45", "http://test.com", self.test_product)
        self.assertEqual(line_item.id, 123456)
        self.assertEqual(line_item.qty, 1)
        self.assertEqual(line_item.cost, 123.45)
        self.assertEqual(line_item.url, "http://test.com")
        self.assertEqual(line_item.product, self.test_product)
        
    def test_from_dict(self):

        line_item = LineItem()
        test_line = {
            "qty": 1,
            "name": "Test Product",
            "url": "http://test.com",
            "cost": "$123.45",
            "id": 123456,
            "product": self.test_product
        }
        line_item.from_dict(test_line)
        self.assertEqual(line_item.id, 123456)
        self.assertEqual(line_item.qty, 1)
        self.assertEqual(line_item.cost, 123.45)
        self.assertEqual(line_item.url, "http://test.com")
        self.assertEqual(line_item.product, self.test_product)
        pass
