import csv
import sys


class JointCsv(object):
  """JointCsv object that stores joint CSV data.

  Methods:
    Dedupe()
    WriteToCsv()
  """

  def __init__(self, input_paths, delimiter=','):
    """Initializes object.

    Args:
      input_paths: List of strings, input paths for files to join. Assumes that
        all the fieldnames of the CSVs are the same.
      delimiter: String, delimiter for CSV file.
    """
    self.data = []
    self.fieldnames = []

    for input_path in input_paths:
      with open(input_path, 'r') as input_file:
        csv_reader = csv.DictReader(input_file, delimiter=delimiter)

        # Make sure that the fieldnames of all the CSVs are the same.
        if not self.fieldnames:
          self.fieldnames = csv_reader.fieldnames
        else:
          assert self.fieldnames == csv_reader.fieldnames

        self.data.extend(csv_reader)

  def Dedupe(self):
    """Dedupes the CSV.

    First keys the data by the contents, then stores the list of the deduped
    data.
    """
    data_keyed_by_contents = {}

    for row in self.data:
      contents = ','.join([value for value in row.values() if value])
      data_keyed_by_contents[contents] = row
    self.data = [row for row in data_keyed_by_contents.values()]

  def WriteToCsv(self, output_path):
    """Writes data to CSV.

    Args:
      output_path: String, path to desired output file.
    """
    with open(output_path, 'w') as output_file:
      csv_writer = csv.DictWriter(output_file, self.fieldnames)
      csv_writer.writeheader()
      csv_writer.writerows(self.data)

  def CompareCsv(self, comparison_csv_path, comparison_columns):
    """Compares comparison CSV to JointCsv Data.

    Args:
      comparison_csv_path: String, path to comparison CSV.
      comparison_columns: List of strings, list of columns to compare.

    Returns:
      Two dictionaries, where the keys are column names and the values are
      a list of column contents that are unique to the named CSV.
    """
    contents_in_joint_csv = {}
    contents_in_comparison_csv = {}
    contents_not_in_joint_csv = {}
    contents_not_in_comparison_csv = {}

    assert set(comparison_columns).issubset(set(self.data[0]))

    with open(comparison_csv_path, 'r') as comparison_file:
      comparison_csv = csv.DictReader(comparison_file)
      assert set(comparison_columns).issubset(set(comparison_csv.fieldnames))

      # Collect all data in comparison CSV.
      for row in comparison_csv:
        for column in comparison_columns:
          contents_in_comparison_csv.setdefault(column, []).append(row[column])

      # Collect all data in joint CSV.
      for row in self.data:
        for column in comparison_columns:
          contents_in_joint_csv.setdefault(column, []).append(row[column])

    for column in comparison_columns:
      contents_not_in_joint_csv[column] = (list(
        set(contents_in_comparison_csv[column]).difference(
          set(contents_in_joint_csv[column]))))
      contents_not_in_comparison_csv[column] = (list(
        set(contents_in_joint_csv[column]).difference(
          set(contents_in_comparison_csv[column]))))

    return contents_not_in_comparison_csv, contents_not_in_joint_csv

  def __str__(self):
    return 'JointCsv has  %s rows, with following fieldnames:\n%s' % (
      len(self.data), self.fieldnames)
