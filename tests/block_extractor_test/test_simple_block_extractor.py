import unittest
import numpy as np
from block_extractor.simple_block_extractor import SimpleBlockExtractor
from type.block.simple_block import SimpleBlock
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from type.cell import cell_type
from type.block.block_type_pmf import BlockTypePMF
from type.block.basic_block_type import BasicBlockType
from type.cell.basic_cell_type import BasicCellType

@DeprecationWarning
class TestSimpleBlockExtractor(unittest.TestCase):
    def testBlockExtractorForSimpleTableWithTwoColumns(self):
        values = np.array([['date', 'value'], ['2001', '10.0'], ['2002', '11.0'], ['2003', '12.0']])
        sheet = Sheet(values, None)
        tags = np.array([[CellTypePMF({BasicCellType.META: 1}), CellTypePMF({BasicCellType.META: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})]])

        sbe = SimpleBlockExtractor()
        blocks = sbe.extract_blocks(sheet, tags)

        # Order of blocks in the list shouldn't actually matter. Write a better test to compare without any known order
        meta = BlockTypePMF(
            {
                BasicBlockType.ATTRIBUTE: 1.0,
            }
        )

        b1 = SimpleBlock("META", 0, 1, 0, 0)
        b2 = SimpleBlock("DATE", 0, 0, 1, 3)
        b3 = SimpleBlock("_DATA_", 1, 1, 1, 3)

        assert blocks[0] == b1
        assert blocks[1] == b2
        assert blocks[2] == b3
