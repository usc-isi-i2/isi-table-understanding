from reader.abstract_file_reader import AbstractFileReader

import xlrd
import logging
import numpy as np
import pyexcel as pyx
from reader.sheet import Sheet
from typing import List


class ExcelReader(AbstractFileReader):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.wb = pyx.get_book(file_name=filename)
        self.wb_xlrd = xlrd.open_workbook(filename)

    def get_sheets(self) -> List[Sheet]:
        for name in self.wb.to_dict():
            values = self.wb[name].to_array()
            values = np.array(values)
            self.fill_merged_cells(values, self.wb_xlrd.sheet_by_name(name).merged_cells)
            yield Sheet(values, {'name': name})

    def get_sheet_by_index(self, idx) -> Sheet:
        values = self.wb.sheet_by_index(idx).to_array()
        values = np.array(values)
        self.fill_merged_cells(values, self.wb_xlrd.sheet_by_index(idx).merged_cells)
        return Sheet(values, None)
        
    # filling the empty cells which are located in the merged cells in reality but are read as empty by pyexcel
    def fill_merged_cells(self, sheet, merged_blocks):
        
        for block in merged_blocks:
            rlo, rhi, clo, chi = block
            val = sheet[rlo][clo]
        
            for rowx in range(rlo, rhi):
                for colx in range(clo, chi):
                    try:
                        sheet[rowx, colx] = val
                    except:
                        # There is a difference in the way xlrd and pyexcel handle merged cells 
                        # Sometimes we end up accessing out of range cells
                        logging.error("Tried to access out of range cell.")
                        break 
