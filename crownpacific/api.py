from queue import Queue
from threading import Thread

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from crownpacific.product import Product, Products
from crownpacific.purchase_order import PurchaseOrder
from crownpacific.result import SearchResult

login_url = r"https://www.cpff.net/my-account/"


class CrownPacificApi(object):

    def __init__(self, username=None, password=None):
        self.verbose = False
        self.username = username
        self.password = password
        self.logged_in = False
        self.session = requests.session()
        self.products = {}
        if username and password:
            self.login(username, password)

    def login(self, username, password):
        self.username = username
        self.password = password
        res = self.session.get(login_url)
        login_soup = BeautifulSoup(res.content, features="lxml")

        nonce = login_soup.find("input", {"id": "woocommerce-login-nonce"})['value']
        payload = "username={user}&" \
                  "password={passwd}&" \
                  "woocommerce-login-nonce={nonce}&" \
                  "wp_http_referer=%2Fmy-account%2F&" \
                  "login=Log+in".format(user=self.username, passwd=self.password, nonce=nonce)
        url = "https://www.cpff.net/my-account/"

        headers = {
            'authority': 'www.cpff.net',
            'origin': 'https://www.cpff.net',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/80.0.3987.87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://www.cpff.net/my-account/',

        }

        # response = requests.request("POST", url, headers=headers, data=payload)
        res = self.session.post(login_url, data=payload, headers=headers)
        login_soup = BeautifulSoup(res.content, features="lxml")
        if not login_soup.find("a", {"class": "login custom"}):
            if self.verbose:
                print("Login failed, costs wont be shown and purchase oders unavailable")
        else:
            self.logged_in = True
            if self.verbose:
                print("Successfully logged in.")
        pass

    def search(self, query):
        items = []
        search_url = r"https://www.cpff.net/?s={query}"
        res = self.rss_search(query)
        for page in res:
            items.append(self.item_page_to_fields(page))
        search_result = SearchResult(query)
        search_result.add_products_by_fields(items)
        return search_result

    def rss_search(self, query):
        items = []
        rss_feed = "https://www.cpff.net/search/{query}/feed/rss2/".format(query=query)
        rss = feedparser.parse(rss_feed)
        pages = self.batch_fetch_pages(x["link"] for x in rss.entries)
        return pages

    def batch_fetch_pages(self, url_list):
        workers = []
        items = []

        def get_page(q):
            while True:
                entry = q.get()
                r = self.session.get(entry)
                if self.verbose:
                    print(entry)
                items.append([entry, r.content])
                q.task_done()

        queue = Queue()
        t_count = 5
        for i in range(t_count):
            worker = Thread(target=get_page, args=(queue,))
            worker.setDaemon(True)
            worker.start()
            workers.append(worker)

        for url in url_list:
            queue.put(url)
        queue.join()

        return items

    def item_page_to_fields(self, page):
        url = page[0]
        contents = page[1]
        if not isinstance(contents, (bytes, str)):
            raise TypeError(f"page must be type bytes or str not {type(contents)}")

        item_soup = BeautifulSoup(contents, features="lxml")
        if item_soup:
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

                fields = {"url": url}

                for idx, field in enumerate(dts):
                    fields[field] = dds[idx]

                # GET PRICING
                for span in detail_soup.find_all("span", {"class": "price"}):
                    field, value = span.text.split(":")
                    fields[field.strip()] = value
                return fields

    def list_purchase_orders(self):
        if not self.logged_in:
            raise Exception("Must be logged in to complete this action")
        orders_page = "https://www.cpff.net/my-account/orders/"
        order_table_class = "woocommerce-orders-table woocommerce-MyAccount-orders shop_" \
                            "table shop_table_responsive my_account_orders account-orders-table"
        res = self.session.get(orders_page)
        orders_soup = BeautifulSoup(res.content, features="lxml")
        order_list_soup = orders_soup.find("table", {"class": order_table_class})
        headers = [x.text for x in order_list_soup.find_all("th")]
        headers.pop(-1)
        headers.append("URL")

        orders = []
        for tr in order_list_soup.find_all("tr"):
            row = []
            for td in tr.find_all("td"):
                row.append(td.text.replace("\t", "").replace("\n", ""))
            if row:
                row.pop(-1)
                row.append(tr.a['href'])
                orders.append(row)
                row[0] = int(row[0].replace("#", ""))
                row[1] = date_parser.parse(row[1]).date()
        return orders

    def get_purchase_order(self, order_number):
        if not self.logged_in:
            raise Exception("Must be logged in to complete this action")

        order_soup = self.retrieve_purchase_order_soup(order_number)
        order_date = order_soup.find("mark", {"class": "order-date"}).text
        order_date = date_parser.parse(order_date).date()
        order_status = order_soup.find("mark", {"class": "order-status"}).text
        total_cost = order_soup.find("span", {"class": "woocommerce-Price-amount amount"}).text
        total_cost = float(total_cost.replace("$", ""))
        total_items = None
        line_items = self.get_purchase_order_line_items(order_number)
        po = PurchaseOrder(line_items)
        po.status = order_status
        po.date = order_date
        po.total_cost = total_cost
        return po

    def retrieve_purchase_order_soup(self, order_number):
        order_url = "https://www.cpff.net/my-account/view-order/{order}/".format(order=order_number)
        res = self.session.get(order_url)
        order_soup = BeautifulSoup(res.content, features="lxml")
        return order_soup

    def get_purchase_order_line_items(self, order_number, order_soup=None):
        if not order_soup:
            order_soup = self.retrieve_purchase_order_soup(order_number)
        order_date = order_soup.find("mark", {"class": "order-date"}).text
        order_status = order_soup.find("mark", {"class": "order-status"}).text
        products_table_class = "woocommerce-table woocommerce-table--order-details shop_table order_details"
        products_soup = order_soup.find("table", {"class": products_table_class})
        line_items = {}
        urls = []
        for tr in products_soup.tbody.find_all("tr"):
            detail_soup, cost_soup = list(tr.find_all("td"))
            # get product link, name, and qty
            cost = cost_soup.span.text
            product_name = detail_soup.a.text.title()
            product_url = detail_soup.a['href']
            urls.append(product_url)
            product_qty = int(detail_soup.strong.text.replace("×", "").strip())
            product_num = int(detail_soup.li.p.text)
            line_item = line_items.setdefault(product_num, {})
            line_item["name"] = product_name
            line_item["url"] = product_url
            line_item["id"] = product_num
            line_item["cost"] = cost
            cur_qty = line_item.setdefault("qty", 0)
            line_item["qty"] = product_qty

        product_pages = self.batch_fetch_pages(urls)
        products = Products()
        for page in product_pages:
            fields = self.item_page_to_fields(page)
            product = Product(fields)
            item = line_items.get(product.item)
            if item:
                item.setdefault("product", product)

        return line_items
