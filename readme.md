# Crown Pacific Foods Website Python API

This project is used for accessing the Crown Pacific Foods website to aquire product information and sales order information

## Usage

```python
from crownpacific.api import CrownPacificApi


api = CrownPacificApi("username", "password")
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

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
