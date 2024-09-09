from reader.abstract_file_reader import AbstractFileReader
import numpy as np
import pyexcel as pyx
from reader.sheet import Sheet
from typing import List


class CsvReader(AbstractFileReader):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.wb = pyx.get_book(file_name=filename)

    def get_sheets(self) -> List[Sheet]:
        for name in self.wb.to_dict():
            values = self.wb[name].to_array()
            values = np.array(values)
            yield Sheet(values, {"path": self.filename, "name": name})

    def get_sheet_by_index(self, idx) -> Sheet:
        values = self.wb.sheet_by_index(idx).to_array()
        values = np.array(values)
        return Sheet(values, {"path": self.filename, "name": idx})
