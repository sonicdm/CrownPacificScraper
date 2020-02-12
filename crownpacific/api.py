import csv
import re
import lxml
from urllib import parse
import dateutil.parser
import feedparser
import atpbar
from threading import Thread
from queue import Queue

import requests
from bs4 import BeautifulSoup, Tag

from crownpacific.util import strings_to_numbers

login_url = r"https://www.cpff.net/my-account/"


class CrownPacificApi(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.products = {}
        self.login()

    def login(self):

        res = self.session.get(login_url)
        login_soup = BeautifulSoup(res.content)

        payload = "username={user}&" \
                  "password={passwd}&" \
                  "woocommerce-login-nonce=5f2e48935d&" \
                  "wp_http_referer=%2Fmy-account%2F&" \
                  "login=Log+in".format(user=self.username, passwd=self.password)
        url = "https://www.cpff.net/my-account/"

        headers = {
            'authority': 'www.cpff.net',
            'origin': 'https://www.cpff.net',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://www.cpff.net/my-account/',

        }

        response = requests.request("POST", url, headers=headers, data=payload)
        res = self.session.post(login_url, data=payload, headers=headers)
        login_soup = BeautifulSoup(res.content)
        pass

    def search(self, query, rss=False):
        items = []
        search_url = r"https://www.cpff.net/?s={query}"
        if rss:
            res = self.rss_search(query)
        else:
            res = self.detailed_search(query).content
        return SearchResult(res, rss)

    def detailed_search(self, query):
        search_url = r"https://www.cpff.net/?s={query}"
        res = self.session.get(search_url.format(query=query))
        return res

    def rss_search(self, query):
        items = []
        workers = []
        rss_feed = "https://www.cpff.net/search/{query}/feed/rss2/".format(query=query)
        rss = feedparser.parse(rss_feed)

        def get_page(q):
            while True:
                entry = q.get()
                item_name = entry["title"].title()
                item_url = entry["link"]
                res = self.session.get(item_url)
                print(item_url)
                items.append([item_url, res.content])
                q.task_done()

        q = Queue()
        t_count = 5
        for i in range(t_count):
            worker = Thread(target=get_page, args=(q,))
            worker.setDaemon(True)
            worker.start()
            workers.append(worker)

        for entry in rss.entries:
            q.put(entry)
        q.join()

        print(items)

        return items

    def get_all_products_by_category(self, category):
        pass


class SearchResult(object):
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

    def __init__(self, result, rss=False):
        self.products = {}
        if rss:
            self.products = self.parse_rss(result)
        else:
            self.products = self.parse_detailed_results(result)

        pass

    def parse_rss(self, res):
        products = {}
        for item in res:
            print(item[0])
            fields = self.item_page_to_fields(item)
            if fields:
                product = self.fields_to_product(fields)
                products[product.upc] = product

        return products

    def item_page_to_fields(self, item):
        item_soup = BeautifulSoup(item[1])
        if item_soup:
            product = Product()
            product_soup = item_soup.find("div", {"class": "row prod-detail"})
            if product_soup:
                detail_soup = list(product_soup.find_all("div"))[1]
                # GET PRODUCT DETAILS
                dts = []
                dds = []
                for dt in list(detail_soup.dl.find_all("dt")):
                    dts.append(dt.text.replace(":", "").strip().replace("\n", ""))

                for dd in list(detail_soup.dl.find_all("dd")):
                    dds.append(dd.text.title())

                fields = {}
                for idx, field in enumerate(dts):
                    fields[field] = dds[idx]

                # GET PRICING
                for span in detail_soup.find_all("span", {"class": "price"}):
                    field, value = span.text.split(":")
                    fields[field.strip()] = value
                return fields

    def fields_to_product(self, fields):
        product = Product()
        for field, value in fields.items():
            setattr(product, self.field_map[field.replace(":", "")], strings_to_numbers(value))

        return product

    def rss_items_to_products(self, items):
        pass

    def parse_detailed_results(self, result):
        items = []
        search_soup = BeautifulSoup(result)
        result_table = search_soup.find("div", {"id": "tblCustomers"})
        for row in result_table.find_all("div", {"class": "row"}):
            for item in row.find_all("div", {"class": "half"}):
                items.append(item)

        return self.items_to_products(items)

    def items_to_products(self, items):
        products = {}
        for item in items:
            fields = self.item_to_fields(item)
            product = self.fields_to_product(fields)
            products[product.item] = product
        return products

    def item_to_fields(self, item):
        """
        :type item: Tag
        :param item:
        :rtype: dict
        """
        # product = Product()
        fields = {}
        # product.brand = str(item.h3.text).title()
        fields["Brand"] = str(item.h3.text).title()
        for tr in item.find_all("tr"):
            field, text = [x.text for x in tr.find_all("td")]
            fields[field] = text
            # setattr(product, self.field_map[field.replace(":", "")], strings_to_numbers(text))

        return fields


class Product(object):

    def __init__(self):
        self.brand = str()
        self._upc = int()
        self.item = int()
        self._pack_size = str()
        self._description = str()
        self.min_qty = int()
        self.srp = float()
        self.case_cost = float()
        self.each_cost = float()
        self.attributes = []

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = str(value).title()

    @property
    def upc(self):
        return self._upc

    @upc.setter
    def upc(self, value):
        self._upc = strings_to_numbers(value[:-1].replace("-", ""))

    def set(self, field, value):
        self.__setattr__(field, value)
        pass
