import abc
import numpy as np
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from typing import List


class CellClassifier(abc.ABC):
    @abc.abstractmethod
    def classify_cells(self, sheet: Sheet) -> 'np.ndarray[CellTypePMF]':  # Single quotes doesn't seem to actually enforce any check.
        pass
