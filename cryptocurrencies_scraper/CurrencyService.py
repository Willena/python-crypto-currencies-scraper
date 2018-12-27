import json
from typing import Dict, List, Optional
import requests


class Currency(object):
    __slots__ = ('symbol', 'name', 'valueUSD', 'valueBTC', 'lastUpdate', 'changes', 'source')

    def __init__(self):
        self.symbol = ""
        self.name = ""
        self.valueUSD = None
        self.valueBTC = None
        self.lastUpdate = None
        self.source = ""
        self.changes = {
            '7d': None,
            '24h': None,
            '1h': None
        }
        # self.chartData = list()

    @staticmethod
    def parse_json(json_data: json, source: str) -> 'Currency':
        new_currency = Currency()
        new_currency.source = source
        new_currency.symbol = json_data['symbol']
        new_currency.name = json_data['name']
        if "additional_values" in json_data.keys():
            new_currency.valueBTC = float(json_data['additional_values']['BTC']['price'])
        if "price_btc" in json_data.keys():
            new_currency.valueBTC = float(json_data['price_btc'])
        new_currency.valueUSD = float(json_data['price_usd'])
        # new_currency.lastUpdate = datetime.fromtimestamp(int(json_data['last_updated'])).strftime('%d-%m-%Y %H:%M:%S')
        new_currency.lastUpdate = int(json_data['last_updated'])
        new_currency.changes = {
            '7d': float(0 if json_data['percent_change_7d'] is None else json_data['percent_change_7d']),
            '24h': float(0 if json_data['percent_change_24h'] is None else json_data['percent_change_24h']),
            '1h': float(0 if json_data['percent_change_1h'] is None else json_data['percent_change_1h'])
        }
        # new_currency.chartData = json_data['chart']

        return new_currency

    def __str__(self) -> str:
        datastr = ''
        datastr += '-' * 5 + self.name + '-' * 5 + '\n'
        datastr += 'Symbol : ' + self.symbol + '\n'
        datastr += 'Value BTC : ' + str(self.valueBTC) + '\n'
        datastr += 'Value USD : ' + str(self.valueUSD) + '\n'
        datastr += 'Last Update : ' + self.lastUpdate + '\n'
        datastr += 'Evolution : ' + str(self.changes) + '\n'
        return datastr

    def get_value(self):
        return self.valueUSD


class NameIndexes:
    instance = None
    fullNameIndex: Dict[str, List[Currency]] = {}

    @classmethod
    def get_instance(cls) -> 'NameIndexes':
        if cls.instance is None:
            cls.instance = NameIndexes()
        return cls.instance

    def __init__(self):
        self.fullNameIndex = {}
        print("INIT")

    def add_to_index(self, curency: Currency):
        if curency.name.lower() in self.fullNameIndex.keys():
            self.fullNameIndex[curency.name.lower()].append(curency)
        else:
            self.fullNameIndex[curency.name.lower()] = [curency]

        if curency.symbol.upper() in self.fullNameIndex.keys():
            self.fullNameIndex[curency.symbol.upper()].append(curency)
        else:
            self.fullNameIndex[curency.symbol.upper()] = [curency]

    def clear_index(self):
        self.fullNameIndex.clear()


class CurrentPriceInterface(object):
    NAME = "DefaultName"

    def __init__(self):
        pass

    def update_currency_list(self):
        pass


class CurrenciesFromCoinMarketCap(CurrentPriceInterface):
    instance = None
    URL_GET_ALL_URRENCIES = 'https://api.coinmarketcap.com/v1/ticker/?limit=3000'
    NAME = "coinmarketcap.com"

    @classmethod
    def get_instance(cls) -> 'CurrenciesFromCoinMarketCap':
        if cls.instance is None:
            cls.instance = CurrenciesFromCoinMarketCap()
        return cls.instance

    def __init__(self):
        super().__init__()

    def update_currency_list(self):
        # print("\t Updating cryptocurrencies values ...")
        self.process_data(requests.get(self.URL_GET_ALL_URRENCIES).json())

    def process_data(self, json_data: json) -> None:
        if type(json_data) is list:
            for el in json_data:
                self.process_data(el)
        else:
            c = Currency.parse_json(json_data, self.NAME)
            NameIndexes.get_instance().add_to_index(c)
        return None


class CurrenciesFromCoin360(CurrentPriceInterface):
    instance = None
    URL_GET_ALL_URRENCIES = 'https://coin360.io/api/v1/coins'
    NAME = "coin360.io"

    @classmethod
    def get_instance(cls) -> 'CurrenciesFromCoin360':
        if cls.instance is None:
            cls.instance = CurrenciesFromCoin360()
        return cls.instance

    def __init__(self):
        super().__init__()

    def update_currency_list(self):
        # print("\t Updating cryptocurrencies values ...")

        self.process_data(requests.get(self.URL_GET_ALL_URRENCIES).json())

    def process_data(self, json_data: json) -> None:
        if type(json_data) is list:
            for el in json_data:
                self.process_data(el)
        else:
            if 'children' in json_data.keys():
                self.process_data(json_data['children'])
            else:
                if 'symbol' in json_data.keys():
                    c = Currency.parse_json(json_data, self.NAME)
                    NameIndexes.get_instance().add_to_index(c)
        return None


class SourceNames:
    COIN360_NAME = CurrenciesFromCoin360.NAME
    COIN_MARKET_CAP_NAME = CurrenciesFromCoinMarketCap.NAME


class Manager:
    price_sources: Dict[str, CurrentPriceInterface] = {}

    def __init__(self):
        self.price_sources[SourceNames.COIN360_NAME] = CurrenciesFromCoin360.get_instance()
        self.price_sources[SourceNames.COIN_MARKET_CAP_NAME] = CurrenciesFromCoinMarketCap.get_instance()
        self.nameIndex = NameIndexes.get_instance()

    def update(self):
        self.nameIndex.clear_index()
        for name, source in self.price_sources.items():
            print("/!\\ Updating " + name + " ... ")
            source.update_currency_list()

        print("Index contains : " + str(len(self.nameIndex.fullNameIndex.keys())) + " keys")

    def get_curency(self, name: str) -> Optional[List[Currency]]:
        if name.lower() in self.nameIndex.fullNameIndex.keys():
            return self.nameIndex.fullNameIndex[name.lower()]
        if name.upper() in self.nameIndex.fullNameIndex.keys():
            return self.nameIndex.fullNameIndex[name.upper()]

        return None

    def add_source(self, new_source: CurrentPriceInterface):
        self.price_sources[new_source.NAME] = new_source

    def remove_source(self, name: str):
        self.price_sources.pop(name, None)

    def all_currencies(self):
        return self.nameIndex.fullNameIndex
