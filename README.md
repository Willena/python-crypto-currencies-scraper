# Python : Simple Crypto currencies scrapper

This is a simple module that retrieve instant crypto 
currencies values in BTC and USD from coin360.com and coinmarketcap apis

### How to use

First install the package

```
pip install cryptocurrencies_scraper
```

#### Basic usage

```python
from cryptocurrencies_scraper.CurrencyService import Manager
manager = Manager() # Create a new instance of the Manager
manager.update() # Ask the manager to update all currencies values

manager.all_currencies() # returns a dict that contain the currency name and symbol as key and currency information as a list
manager.get_curency('btc') # return the list of currency values retrived for bitcoin using symbol
manager.get_curency('bitcoin') # return the list of currency values retrived for bitcoin using name
```

#### Add your own scraper

A scraper should extends the `CurrentPriceInterface`.
Here is a basic scheme for a new scraper

```python

class MySourceForCurrencies(CurrentPriceInterface):
    instance = None
    URL = 'https://api.mysource.com/v1/ticker/?limit=3000'
    NAME = "mysource.com"

    @classmethod
    def get_instance(cls) -> 'CurrenciesFromCoinMarketCap':
        if cls.instance is None:
            cls.instance = MySourceForCurrencies()
        return cls.instance

    def __init__(self):
        super().__init__()

    def update_currency_list(self):
        self.process_data(requests.get(self.URL).json())

    def process_data(self, json_data: json) -> None:
        # Manipulate the the json to be Currency "parsable"
        c = Currency.parse_json(json_data, self.NAME)
        #When parsed, add it to the index 
        NameIndexes.get_instance().add_to_index(c)
        return None

```

In order for your scraper to be working you need to add it to the manager

```python
from cryptocurrencies_scraper.CurrencyService import Manager
manager = Manager()
manager.add_source(MySourceForCurrencies.get_instance())

# you can also remove a source
manager.remove_source(MySourceForCurrencies.NAME)

```

Then on each `manager.update()` call your scraper will be called and currencies added to the Index

#### NameIndex

This class is used internally to index all currencies. 
When a new currency is added, it will be grouped by the symbol and the name (symbol upper, name lower case)

The only useful method is `NameIndexes.get_instance().add_to_index(currency)`. On each update, it get completlly cleared 
from all old values.


#### `Currency`

This is the object that represent one currency here is the structure

```json
 {
    "symbol" : "BTC",
    "name" : "Bitcoin",
    "valueUSD" : 5513,
    "valueBTC": 1,
    "lastUpdate" : 1566531513813,
    "source" : "coin360.com",
    "changes" : {
        "7d": -1,
        "24h": -5,
        "1h": -10
    }
 }
```

