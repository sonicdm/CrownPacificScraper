from crownpacific.product import Products


class PurchaseOrder(Products):
    def __init__(self, line_items_dict=None):
        super().__init__()
        self._line_items = {}
        if line_items_dict:
            self.add_line_items_from_dict(line_items_dict)
        pass

    def add_line_items_from_dict(self, line_items):
        for product_num, detail in line_items.items():
            self.add_line_item_from_dict(detail)

    def add_line_item_from_dict(self, line_item_dict):

        line_item = self._line_items.setdefault(
            line_item_dict['id'],
            self.add_new_line_item(line_item_dict['id'], from_dict=line_item_dict)
        )

        line_item.qty += line_item_dict['qty']
        self._line_items[line_item.id] = line_item

    def add_new_line_item(self, product_num=None, qty=0, cost=0, url=None, product=None, from_dict=None):

        line_item = self._line_items.get(product_num)
        if line_item:
            line_item.qty += qty
        else:
            line_item = LineItem(product_num, qty, cost, url, product, from_dict)

        self._line_items[product_num] = line_item
        self.add_product(line_item.product)

    def add_line_item(self, line_item):
        self._line_items[line_item.id] = line_item

    def add_line_items(self, items):
        """
        Import a tuple or list of arguments for new items:
        [product_num, qty, cost, url, product]
        OR
        a list of LineItem objects
        :param items:
        :return:
        """
        for item in items:
            if isinstance(item, LineItem):
                self.add_line_item(item)
            if isinstance(item, (list, tuple)):
                self.add_new_line_item(*item)

    @property
    def values(self):
        return [x.values for x in self._line_items.values()]

    @property
    def line_items(self):
        return list(self._line_items.values())

    def __len__(self):
        return len(self._line_items)


class LineItem:
    def __init__(self, product_num=None, qty=0, cost=0, url=None, product=None, from_dict=None):
        self.qty = qty
        self.id = product_num
        self.url = url
        self.product = product
        self._cost = 0
        self.cost = cost
        if from_dict:
            self.from_dict(from_dict)

    def from_dict(self, line_item_dict):
        for k, v in line_item_dict.items():
            setattr(self, k, v)

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        if isinstance(value, str):
            self._cost = float(value.strip("$"))
        else:
            value = float(value)

    @property
    def values(self):
        return [self.id, self.qty, self.cost, self.url, self.product]
