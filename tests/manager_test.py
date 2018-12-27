from time import time

from cryptocurrencies_scraper.CurrencyService import Manager

if __name__ == '__main__':
    manager = Manager()
    timestart = time()
    manager.update()
    print(str(time() - timestart) + "s to update")

    print(manager.all_currencies())
    timestart = time()
    print(str(manager.get_curency('btc')))
    print(str(time() - timestart) + "s to get one currency")
    print(str(manager.get_curency('bitcoin')))
