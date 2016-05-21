import csv
import math
import re

from blacklist_generator import BlacklistGenerator
import portfolio_constants as const


class Stock(object):
  """Stock object that contains information about a given stock.

  Methods:
    CleanUpStockData: Cleans up the data in the stock object.
    ToDict: Returns dict version of stock object.
  """

  def __init__(self, symbol, price, stock_data=None):
    """Initialize object.

    Args:
      symbol: String, Stock symbol.
      price: Int, Price of stock.
      stock_data: Dict, with all the information about the given stock.

    """
    self.symbol = symbol
    self.price = price
    self.stock_data = stock_data
    self.stock_data['GoogleUrl'] = const.BASE_GOOGLE_URL % self.symbol
    self.stock_data['SecUrl'] = const.BASE_SEC_URL % self.symbol
    
  def CleanUpStockData(self):
    """Cleans up data in the stock object.
    """
    for key, value in self.stock_data.iteritems():
      if isinstance(value, str):
        for char in const.CHARS_TO_REMOVE:
          value.replace(char, '')
        self.stock_data[key] = value
        if re.search('\d[\d.]*T$', value):
          self.stock_data[key] = float(value.strip('T')) * math.pow(10, 12)
        if re.search('\d[\d.]*B$', value):
          self.stock_data[key] = float(value.strip('B')) * math.pow(10, 9)
        elif re.search('\d[\d.]*M$', value):
          self.stock_data[key] = float(value.strip('M')) * math.pow(10, 6)
        elif re.search('\d[\d.]*K$', value):
          self.stock_data[key] = float(value.strip('K')) * math.pow(10, 3)

  def ToDict(self):
    """Convert stock object into dictionary. Useful for writing to CSV."""
    return {var: self.stock_data.get(var, '') 
            for var in const.VARS_OF_INTEREST}


class Portfolio(object):
  """Portfolio object that stores groups of stock objects.

  Methods:
    AddStockDict: Adds a dict full of stocks to the portfolio.
    AddStockObjects: Adds a list of stock objects to the portfolio.
    SortStocks: Sorts the portfolio given a key function.
    BlacklistBySymbol: Remove blacklisted stocks from portfolio by symbol.
    BlacklistBySector: Remove blacklisted stocks from portfolio by sector.
    CleanUpStocks: Clean up stock data.
  """

  def __init__(self, name, blacklist):
    """Inits object.

    Args:
      name: string, Name of portfolio.
      blacklist: blacklist generator object, Blacklist generator instance.
    """
    self.name = name
    self.stocks = []
    self._blacklist = blacklist

  def AddStockDict(self, data):
    """Adds a dict full of stocks to the portfolio.

    data: dict, Dict with stock information. Key is the stock symbol,
    value is a data dict with stock information.
    """
    passed_stock_creation = []
    failed_stock_creation = []

    # Create and add stock objects to portfolio.
    for symbol, stock_data in data.iteritems():
      try:
        # The assumption here is that if there is no entry in market 
        # capitalization, it is probably not the type of stock we're interested 
        # in. Same with the stock price.
        assert (stock_data[const.MARKET_CAPITALIZATION_KEY] and 
                stock_data[const.MARKET_CAPITALIZATION_KEY] != 'N/A' and
                float(stock_data[const.PRICE_KEY]) != 0.0)
                
        stock = Stock(stock_data[const.SYMBOL_KEY],
                      stock_data[const.PRICE_KEY],
                      stock_data)
        self.stocks.append(stock)
        passed_stock_creation.append(symbol)
      except:
        failed_stock_creation.append(symbol)

    # Update and print blacklist information.
    print '%s of %s failed stock creation.' % (len(failed_stock_creation),
                                               len(data))
    self._blacklist.UpdateBlacklist(passed_stock_creation,
                                    failed_stock_creation)

  def CleanUpStocks(self):
    """Cleans up stock data.
    """
    for stock in self.stocks:
      stock.CleanUpStockData()
  
  def AddStockObjects(self, list_of_stocks):
    """Adds a list of stock objects to the portfolio.

    Args:
      list_of_stocks: List of stock objects.
    """
    self.stocks.extend(list_of_stocks)

  def SortStocks(self, key, reverse=False):
    """Sorts the portfolio given a key function.

    Args:
      key: Function, sort key.
      reverse: Boolean, whether reverse sorting should be used.
    """
    self.stocks = sorted(self.stocks, key=key, reverse=reverse)

  def BlacklistBySymbol(self, symbol_blacklist):
    """Remove blacklisted stocks from portfolio by symbol.

    Args:
      symbol_blacklist: List of strings, blacklisted stock symbols.
    """
    self.stocks = [stock for stock in self.stocks
                   if stock.symbol not in symbol_blacklist]

  def BlacklistBySector(self, sector_blacklist):
    """Remove blacklisted stocks from portfolio by sector.

    Args:
      attribute_blacklist: List of strings, blacklisted stock sectors.
    """
    self.stocks = [stock for stock in self.stocks
                   if stock.sector not in sector_blacklist]

  def WriteToCsv(self, path_to_outfile):
    """Write portfolio to CSV."""
    with open(path_to_outfile, 'w') as ofile:
      writer = csv.DictWriter(ofile, const.VARS_OF_INTEREST)
      writer.writeheader()
      for stock in self.stocks:
        writer.writerow(stock.ToDict())
