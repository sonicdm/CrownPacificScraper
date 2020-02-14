import random
from unittest import TestCase

from crownpacific.api import CrownPacificApi
from crownpacific.product import Product
from crownpacific.purchase_order import PurchaseOrder, LineItem
import os

def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return random.randint(range_start, range_end)


class TestPurchaseOrder(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = CrownPacificApi(os.getenv("cp_username"), os.getenv("cp_password"))
        cls.line_items_dict = cls.api.get_purchase_order_line_items(1240519)

    def setUp(self):
        self.test_product = Product()
        self.test_product.brand = "Test"
        self.test_product.upc = "123456-12345"
        self.test_product.case_cost = "$12.34"
        self.test_product.each_cost = "$1.23"
        self.test_product.item = 123456
        self.test_product.srp = "2.34"
        self.test_product.attributes = "Test Attribute 1, Test Attribute 2"
        self.test_line_item = LineItem(123456, 1, "$123.45", "http://test.com", self.test_product)
        self.test_products = [x['product'] for x in self.line_items_dict.values()]

        line_items_count = 10
        self.line_items_list = []
        self.line_items = []
        used = []
        for line in range(line_items_count):
            random_product = random.choice(self.test_products)
            while random_product in used:
                random_product = random.choice(self.test_products)
            used.append(random_product)
            po_num = random_with_n_digits(6)
            cost = round(random.uniform(50, 300), 2)
            url = "Http://test.com/" + str(random_with_n_digits(6))
            qty = random.randint(0, 10)
            self.line_items.append(LineItem(po_num, qty, cost, url, random_product))
            self.line_items_list.append([random_product.item, qty, cost, url, random_product])

        self.random_line_item_dict = random.choice(list(self.line_items_dict.values()))

    def test___init__(self):
        purchase_order = PurchaseOrder(self.line_items_dict)
        self.assertEqual(len(purchase_order), len(self.line_items_dict))

    def test_add_line_items_from_dict(self):
        purchase_order = PurchaseOrder()
        purchase_order.add_line_items_from_dict(self.line_items_dict)

    def test_add_line_item_from_dict(self):
        purchase_order = PurchaseOrder()
        purchase_order.add_line_item_from_dict(self.random_line_item_dict)
        self.assertIn(self.random_line_item_dict['id'], purchase_order._line_items.keys())

    def test_add_line_item(self):
        purchase_order = PurchaseOrder()
        purchase_order.add_line_item(self.test_line_item)
        self.assertIn(self.test_line_item, purchase_order.line_items)

    def test_add_line_items_from_list_of_args(self):
        purchase_order = PurchaseOrder()
        purchase_order.add_line_items(self.line_items_list)
        for x in self.line_items_list:
            print(x)
        self.assertEqual(len(self.line_items_list), len(purchase_order))

    def test_add_line_items_from_list_of_line_items(self):
        purchase_order = PurchaseOrder()
        purchase_order.add_line_items(self.line_items)
        self.assertEqual(len(self.line_items), len(purchase_order))

    def test_values(self):
        purchase_order = PurchaseOrder(self.line_items_dict)
        print(purchase_order.values)
