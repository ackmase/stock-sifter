"""Generates and updates blacklist for stock symbols."""

import csv
import portfolio_constants as const


class BlacklistGenerator(object):
  """Module for generating and updating blacklisted stock symbols.

  Methods:
    GetBlacklist: Generates a blacklist using historical stock data.
    UpdateBlacklist: Updates blacklist using success and failure symbol lists.
  """
  
  def __init__(self, minimum_failures, success_to_failure_ratio,
               symbol_data_path):
    """Inits.

    Args:
      minimum_failures: int, Minimum number of failures before symbol can be
        considered for blacklisting.
      success_to_failure_ratio: float, the less than or equal to threshold for
        when to consider a symbol blacklisted. For example, if this ratio is 0.2
        and there is 1 success to 5 failures for the symbol, it will be
        blacklisted
      symbol_data_path: string, Path to symbol data CSV.
    """
    self._minimum_failures = int(minimum_failures)
    self._success_to_failure_ratio = float(success_to_failure_ratio)
    self._symbol_data_path = symbol_data_path
    self._symbol_data = list(self._GetSymbolData())

  def _GetSymbolData(self):
    """Get symbol data from CSV.

    This method needs to yield a CSV line so that the data doesn't get lost
    when we leave the "with" statement.

    Yields:
      Single CSV line."""
    
    with open(self._symbol_data_path, 'r') as symbol_file:
      symbol_reader = csv.DictReader(symbol_file)
      for row in symbol_reader:
        yield row

  def GetBlacklist(self):
    """Gets symbol blacklist according to object's thresholds.

    Returns:
      List of strings that contains blacklisted stock symbols.
    """
    blacklist = []

    if self._symbol_data:
      for row in self._symbol_data:
        failures = int(row[const.FAILURE_KEY])
        successes = int(row[const.SUCCESS_KEY])

        if (failures and
            int(failures) >= int(self._minimum_failures) and
            float(successes)/float(failures) < self._success_to_failure_ratio):
          blacklist.append(row[const.SYMBOL_KEY])

    return blacklist
        
  def UpdateBlacklist(self, success_symbols, fail_symbols):
    """Update stock symbol data using given failure and success records.

    Args:
      success_symbols: list of strings, List of symbols that succeeded.
      fail_symbols: list of strings, List of failed symbols.
    """
    to_write = []
    symbol_to_data = {}

    with open(self._symbol_data_path, 'w') as symbol_file:
      symbol_writer = csv.DictWriter(symbol_file, const.SYMBOL_DATA_HEADER)

      if self._symbol_data:
        symbol_to_data = {row[const.SYMBOL_KEY]: row
                          for row in self._symbol_data}

      for symbol in success_symbols:
        if symbol not in success_symbols:
          to_write.append(self._CreateCsvLine(symbol, 1, 0))

      for symbol in fail_symbols:
        if symbol not in symbol_to_data:
          to_write.append(self._CreateCsvLine(symbol, 0, 1))

      for symbol, row in symbol_to_data.iteritems():
        if symbol in success_symbols:
          row[const.SUCCESS_KEY] = 1 + int(row[const.SUCCESS_KEY])
        if symbol in fail_symbols:
          row[const.FAILURE_KEY] = 1 + int(row[const.FAILURE_KEY])

      symbol_writer.writeheader()
      symbol_writer.writerows(to_write)
      symbol_writer.writerows(symbol_to_data.itervalues())

  @staticmethod
  def _CreateCsvLine(symbol, successes, failures):
    """Creates a CSV given a symbol, successes, and failures.

    Args:
      symbol: string, Stock symbol.
      successes: int, Number of successes.
      failures: int, Number of failures.

    Returns:
      A dict representation of a CSV line.
    """
    return {const.SYMBOL_KEY: symbol,
            const.SUCCESS_KEY: successes,
            const.FAILURE_KEY: failures}

def BackfillBlacklist(symbol_data_path, boost_failure_threshold,
                      boost_failures_by):
  """Backfill the symbol data by boosting failures.

  Args:
    symbol_data_path: string, Path to symbol data CSV.
    boost_failure_threshold: int, Greater than threshold for which stocks to
      boost failure rates of. For example, if this threshold is 0, any stock
      that has more than 0 failures will be boosted by the boost_failure_by
      input.
    boost_failures_by: int, Number to boost failures by.
  """
  to_write = []

  with open(symbol_data_path, 'r') as symbol_file:
    symbol_reader = csv.DictReader(symbol_file)
    for row in symbol_reader:
      failures = int(row[const.FAILURE_KEY])
      if failures > boost_failure_threshold:
        row[const.FAILURE_KEY] = failures + boost_failures_by
      to_write.append(row)

    with open(const.SYMBOL_DATA_PATH, 'w') as symbol_file:
      symbol_writer = csv.DictWriter(symbol_file, const.SYMBOL_DATA_HEADER)
      symbol_writer.writeheader()
      symbol_writer.writerows(to_write)


if __name__ == '__main__':
  BackfillBlacklist(const.SYMBOL_DATA_PATH, const.BOOST_FAILURE_THRESHOLD,
                    const.BOOST_FAILURES_BY)
