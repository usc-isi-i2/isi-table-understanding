import abc
from typing import List
from type.block.simple_block import SimpleBlock
import numpy as np
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF

class BlockExtractor(abc.ABC):
    @abc.abstractmethod
    def extract_blocks(self, sheet: Sheet, tags: 'np.array[CellTypePMF]') -> List[SimpleBlock]:
        pass
