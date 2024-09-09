from reader.csv_reader import CsvReader
from reader.excel_reader import ExcelReader



# TODO: Is there a better way to return the correct reader class?
def get_file_reader(filename):
    if filename.endswith(".xls") or filename.endswith(".xlsx"):
        return ExcelReader(filename)
    elif filename.endswith(".csv"):
        return CsvReader(filename)
