import unittest
import numpy as np
from type.block.simple_block import SimpleBlock
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from type.cell import cell_type
from block_extractor.example_block_extractor import ExampleBlockExtractor
from type.block.block_type_pmf import BlockTypePMF
from type.block.basic_block_type import BasicBlockType
from type.cell.basic_cell_type import BasicCellType


class TestExampleBlockExtractor(unittest.TestCase):
    def testBlockExtractorForSimpleTableWithTwoColumns(self):

        values = np.array([['date', 'value'], ['2001', '10.0'], ['2002', '11.0'], ['2003', '12.0']])
        sheet = Sheet(values, None)
        tags = np.array([[CellTypePMF({BasicCellType.META: 1}), CellTypePMF({BasicCellType.META: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})]])

        sbe = ExampleBlockExtractor()
        blocks = sbe.extract_blocks(sheet, tags)

        # Order of blocks in the list shouldn't actually matter. Write a better test to compare without any known order
        bc = BlockTypePMF(
            {
                BasicBlockType.ATTRIBUTE: 0.9,
                BasicBlockType.HEADER: 0.1,
                # block_type.EMPTY: 0
            }
        )

        b1 = SimpleBlock(bc, 0, 1, 0, 3)

        assert blocks[0] == b1
