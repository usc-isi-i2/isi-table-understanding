from cell_classifier.cell_classifier import CellClassifier
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from type.cell.basic_cell_type import BasicCellType
import numpy as np


class ExampleCellClassifier(CellClassifier):
    def __init__(self):
        pass

    def classify_cells(self, sheet: Sheet) -> 'np.ndarray[CellTypePMF]':
        cell_classification = {
            BasicCellType.EMPTY: 0.9,  # Probability distribution of cell types
            BasicCellType.META: 0.1 # etc
            # cell_type.DATA: 0
            # cell_type.DATE: 0
        }

        table_class = np.full(sheet.values.shape, CellTypePMF(cell_classification))

        return table_class
