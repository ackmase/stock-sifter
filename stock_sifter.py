import csv
import json

from blacklist_generator import BlacklistGenerator
from portfolio import Portfolio
import portfolio_constants as const
import time
import urllib

import re


def FormYahooUrlsInBatches(stock_symbols, batch_size):
  """Form Yahoo Finance query URL with given stock symbols.

  Args:
    stock_symbols: List of strings, stock symbols.
    batch_size: Int, maximum size of each batch.

  Returns:
    A list of Url strings.
  """
  urls = []

  # Process stock symbols in batches.
  while stock_symbols:
    current_batch = stock_symbols[:batch_size]
    stock_symbols = stock_symbols[batch_size:]

    # Form URLs.
    quoted_symbols = ['%s%s%s' % (const.QUOTE_ESCAPE,
                                  symbol,
                                  const.QUOTE_ESCAPE)
                      for symbol in current_batch]
    stock_list_string = const.COMMA_ESCAPE.join(quoted_symbols)
    urls.append(const.BASE_YAHOO_URL % (stock_list_string))

  return urls


def GrabStockInformationFromCsv(path, symbol_key, blacklist=None):
  """Grabs stock information from a CSV file.

  Args:
    path: string, Path to the input CSV.
    symbol_key: string, The CSV header name that contains the symbols.
    blacklist: blacklist generator object. If present, leave out blacklisted
      stocks.
    
  Returns:
    Dict with stock symbols as keys and a data dict as values.
  """
  with open(path, 'r') as input_file:
    stock_csv = csv.DictReader(input_file)

    if blacklist:
      blacklist_symbols = blacklist.GetBlacklist()
      return {row[symbol_key]: row for row in stock_csv
              if row[symbol_key] not in blacklist_symbols}
    else:
      return {row[symbol_key]: row for row in stock_csv}


def GrabStockInformationFromYahoo(symbols, batch_size, blacklist=None):
  """Grabs stock information from Yahoo.

  Args:
    symbols: list of strings, List of stock symbols.
    batch_size: int, Size of batches allowed by Yahoo.
    blacklist: blacklist generator object, If present, leave out blacklisted
      stocks.

  Returns:
    Dict with stock symbols as keys and a data dict as values.
  """
  symbol_to_data = {}

  # Remove blacklisted stocks if requested.
  if blacklist:
    symbols = list(set(symbols).difference(set(blacklist.GetBlacklist())))

  # Get Yahoo query URLs.
  urls = FormYahooUrlsInBatches(symbols, batch_size)

  for url in urls:
    # Process Yahoo JSON output.
    json_raw_dump = urllib.urlopen(url).read()
    json_formed_dump = json.JSONDecoder().decode(json_raw_dump)
    raw_quotes = json_formed_dump['query']['results']['quote']

    # Update data dict with stock information.
    if isinstance(raw_quotes, list):
      symbol_to_data.update(
        {data[const.SYMBOL_KEY]: data for data in raw_quotes})
    else:
      symbol_to_data.update({raw_quotes[const.SYMBOL_KEY]: raw_quotes})

    # Wait a few seconds to avoid rate limits.
    time.sleep(5)

  return symbol_to_data


def main():
  # Initialize blacklist object.
  blacklist = BlacklistGenerator(const.MINIMUM_FAILURES,
                                 const.SUCCESS_TO_FAILURE_RATIO,
                                 const.SYMBOL_DATA_PATH)

  # Get data from NASDAQ.
  symbol_to_nasdaq_data = GrabStockInformationFromCsv(
    const.STOCK_SYMBOL_PATH % '',
    const.SYMBOL_KEY,
    blacklist=blacklist)

  # Add data from Yahoo.
  symbol_to_yahoo_data = GrabStockInformationFromYahoo(
    symbol_to_nasdaq_data.keys(),
    const.MAX_SYMBOLS,
    blacklist=blacklist)

  # Join NASDAQ and Yahoo data.
  symbol_to_data = symbol_to_nasdaq_data
  for symbol, yahoo_data in symbol_to_yahoo_data.iteritems():
    default_nasdaq_data = {key: 'n/a' for key in const.NASDAQ_CONSTANTS}
    symbol_to_data.get(symbol, default_nasdaq_data).update(yahoo_data)
              
  # Construct and print portfolio out to CSV.
  portfolio = Portfolio('Whole Portfolio', blacklist)
  portfolio.AddStockDict(symbol_to_data)
  #portfolio.BlacklistBySector(const.SECTOR_BLACKLIST)
  portfolio.CleanUpStocks()
  portfolio.WriteToCsv('%s%s%s%s.csv' %(
      const.BASE_PATH, 
      const.DATA_SUB_PATH,
      'stock_data_',
      time.strftime('%Y-%m-%d', time.localtime())))



if __name__ == '__main__':
  main()

