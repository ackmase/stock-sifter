import time
import urllib

import portfolio_constants as const

URLS = [const.SYMBOL_SCRAPE_URL,
        const.STOCKS_OF_INTEREST_URL]

FILE_PATHS = [const.NASDAQ_STOCK_SYMBOL_PATH,
              const.STOCKS_OF_INTEREST_PATH]


def main():
  assert len(URLS) == len(FILE_PATHS)
  
  for index in range(len(URLS)):
    urllib.urlretrieve(URLS[index], FILE_PATHS[index])
    time.sleep(3)
  print 'Stock symbol data retrieved.'


if __name__ == '__main__':
  main()
