import unittest
from reader.csv_reader import CsvReader
from reader.excel_reader import ExcelReader
from reader.file_reader import get_file_reader

## Run as python -m unittest tests.reader_test.test_file_reader

class TestCSVReader(unittest.TestCase):
    def testCorrectReaderClassIsReturned(self):
        reader = get_file_reader("tests/data/test.csv")
        assert isinstance(reader, CsvReader)

        reader = get_file_reader("tests/data/test.xls")  # TODO: add test.xls file to data/
        assert isinstance(reader, ExcelReader)

        reader = get_file_reader("tests/data/test.xlsx")  # TODO: add test.xlsx file to data/
        assert isinstance(reader, ExcelReader)
