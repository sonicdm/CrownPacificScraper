from bs4 import BeautifulSoup

from crownpacific.product import Product, Products
from crownpacific.util import strings_to_numbers


class SearchResult(Products):

    def __init__(self, query=None):
        super().__init__()
        self.query = query

    @property
    def results(self):
        return len(self._products)

    def __repr__(self):
        return f"crownprince.result.SearchResult({self.query})"

    def __str__(self):
        return f"Search result for {self.query}. {self.results} results. {self.products}"


