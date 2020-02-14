# Crown Pacific Foods Website Python API

This project is used for accessing the Crown Pacific Foods website to aquire product information and sales order information

## Usage

### Searching for products
basic searches without cost info can be done without login
```python
from crownpacific.api import CrownPacificApi


api = CrownPacificApi("username", "password") 
print(api.logged_in) # check if login was successful returns True or False
api.verbose = True # enable text output
search = api.search("Test Search")  # searches database for search term and returns a SearchResult
print(search.query)  # returns "Test Search"
print(search.results)  # returns the number of results found '4'
products = search.products  # returns a Products object containing the found products
product = products[0]  # gives you a Product object with item metadata

print(product)  # print out the product values
# {
#   'item': 12345, 'brand': 'Test', 'description': 'Test Description', 'upc': 12345612345,
#   'pack_size': '1 / 12 / 2.5 / Oz *', 'each_cost': 1.23, 'case_cost': 12.34,
#   'min_qty': 0, 'srp': 1.99, 'attributes': ['']
# }
# fetching product properties
print(product.description)  # "Test Description"
print(product.brand)  # "Test"
print(product.srp)  # 1.99

```

### Purchase Orders
All purchase order operations require an account
```python
from crownpacific.api import CrownPacificApi
api = CrownPacificApi("username", "password") 
print(api.list_purchase_orders())
# [['#12345', '7 February, 2020', 'Completed', '$1,234.56 for 44 items','https://www.cpff.net/my-account/view-order/12345/']]
order = api.get_purchase_order(12345) # get purchase order #12345
products = order.products # same as with search 
line_items = order.line_items # returns a set of line items
line_item = line_items[0]
# get line item properties
qty = line_item.qty
total_cost = line_item.cost
product_number = line_item.id
product_url = line_item.url
product = line_item.product # returns a Product result for the line item containing details
```

### Products
```python
from crownpacific.product import Products
# Products Object
products = Products()

# get products a Products object containing products by brand from the collection
brand_products = products.get_products_by_brand("test brand")

# get a product by UPC
product = products.get_product_by_upc(12345612345)

# get products by any field
products_by_cost = products.get_products_by_field("each_cost", 1.23) # return all products that cost 1.23
```



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
