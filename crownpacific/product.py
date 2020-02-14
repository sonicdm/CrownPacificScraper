from crownpacific.util import strings_to_numbers


class Product(object):
    field_map = {
        "Item": "description",
        "Description": "description",
        "UPC": "upc",
        "Pack Size": "pack_size",
        "Item#": "item",
        "Item Number": "item",
        "SRP": "srp",
        "Case Cost": "case_cost",
        "Each Cost": "each_cost",
        "Attributes": "attributes",
        "Brand": "brand",
    }

    def __init__(self, fields=None):
        self.min_qty = 0
        if fields:
            self.fields_to_product(fields)
        else:
            self.brand = str()
            self._upc = int()
            self.item = int()
            self.pack_size = str()
            self._description = str()
            self.min_qty = int()
            self.srp = float()
            self.case_cost = float()
            self.each_cost = float()
            self._attributes = []

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = str(value).title().replace("\n", "")

    @property
    def upc(self):
        return self._upc

    @upc.setter
    def upc(self, value):
        if isinstance(value, str):
            self._upc = strings_to_numbers(value[:-1].replace("-", ""))
        else:
            self._upc = value

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        if isinstance(value, list):
            self._attributes = value
        elif isinstance(value, str):
            self._attributes = value.split(",")
        else:
            raise ValueError("Attributes must be string or list of strings")

    def set(self, field, value):
        self.__setattr__(field, value)
        pass

    def fields_to_product(self, fields):
        for field, value in fields.items():
            setattr(self, self.field_map[field.replace(":", "")], strings_to_numbers(value))

    @property
    def values(self):
        return {
            "item": self.item,
            "brand": self.brand,
            "description": self.description,
            "upc": self.upc,
            "pack_size": self.pack_size,
            "each_cost": self.each_cost,
            "case_cost": self.case_cost,
            "min_qty": self.min_qty,
            "srp": self.srp,
            "attributes": self.attributes
        }

    def __str__(self):
        return f"Brand: {self.brand} Description: {self.description} " \
            f"UPC: {self.upc} Cost: {self.each_cost} SRP: {self.srp}"

    def __repr__(self):
        return f"crownpacific.product.Product {self.brand} {self.description} {self.upc}"


class Products(object):
    def __init__(self):
        self._products = {}

    def add_product_by_fields(self, fields):
        """
        :type fields: dict
        :param fields: mapped fields
        :return:
        """
        product = Product(fields)
        self._products[product.item] = product

    def add_products_by_fields(self, products):
        for product_fields in products:
            self.add_product_by_fields(product_fields)

    def add_product(self, product):
        """
        :type product: Product
        :param product:
        :return:
        """
        if isinstance(product, Product):
            self._products[product.item] = product

    def add_products(self, products):
        for product in products:
            self.add_product(product)

    def get_product_by_upc(self, upc):
        for product in self._products.values():
            if product.upc == upc:
                return product

    def get_products_by_field(self, field, value):
        products = Products()
        for product in self._products.values():
            attr = getattr(product, field)
            if isinstance(attr, str) and isinstance(value, str):
                value = value.lower()
                attr = attr.lower()
            if attr == value:
                products.add_product(product)

        return products

    @property
    def products(self):
        return list(self._products.values())

    def get_products_by_brand(self, brand):
        return self.get_products_by_field("brand", brand.lower())

    def __len__(self):
        return len(self._products)

    def __str__(self):
        return str(self.products)
