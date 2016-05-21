import csv
import os
import sys

import join_files
import portfolio_constants as const


INPUT_PATHS = [const.NASDAQ_STOCK_SYMBOL_PATH, const.NASDAQ_STOCK_SYMBOL_PATH]

OUTPUT_PATH = const.STOCK_SYMBOL_PATH % ''

OLD_OUTPUT_PATH = const.STOCK_SYMBOL_PATH % '_old'

SYMBOL_KEY = 'Symbol'

def main():
  joint_csv = join_files.JointCsv(INPUT_PATHS, '|')
  joint_csv.Dedupe()
  joint_csv.WriteToCsv(OUTPUT_PATH)
  new_stocks_dict, retired_stocks_dict = joint_csv.CompareCsv(OLD_OUTPUT_PATH,
                                                              [SYMBOL_KEY])
  new_stocks = new_stocks_dict[SYMBOL_KEY]
  retired_stocks = retired_stocks_dict[SYMBOL_KEY]
  
  if not new_stocks and not retired_stocks:
    print '<b>No new stocks, no retired stocks.</b>'
  else:
    print 'New stocks: %s' % new_stocks
    print 'Retired stocks: %s' % retired_stocks

  print '\n%s' % joint_csv

if __name__ == '__main__':
  main()
