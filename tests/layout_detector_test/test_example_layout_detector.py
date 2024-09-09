import unittest
import numpy as np
from type.cell.cell_type_pmf import CellTypePMF
from type.block.simple_block import SimpleBlock
from layout_detector.example_layout_detector import ExampleLayoutDetector
from reader.sheet import Sheet
from type.cell.basic_cell_type import BasicCellType

from type.block.block_type_pmf import BlockTypePMF
from type.block.basic_block_type import BasicBlockType
from type.layout.basic_edge_type import BasicEdgeType

class TestExampleLayoutDetector(unittest.TestCase):
    def testLayoutDetectionForSimpleTableWithTwoColumns(self):

        values = np.array([['date', 'value'], ['2001', '10.0'], ['2002', '11.0'], ['2003', '12.0']])
        sheet = Sheet(values, None)
        tags = np.array([[CellTypePMF({BasicCellType.META: 1}), CellTypePMF({BasicCellType.META: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})],
                         [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})]])

        ATTRIBUTE = BlockTypePMF({BasicBlockType.ATTRIBUTE: 1.0})
        VALUE = BlockTypePMF({BasicBlockType.VALUE: 1.0})

        b1 = SimpleBlock(ATTRIBUTE, 0, 1, 0, 0)
        b2 = SimpleBlock(ATTRIBUTE, 0, 0, 1, 3)  # Todo: This is not correct
        b3 = SimpleBlock(VALUE, 1, 1, 1, 3)

        blocks = [b1, b2, b3]

        sld = ExampleLayoutDetector()
        layout = sld.detect_layout(sheet, tags, blocks)

        # TODO: The labels assigned to the edges here are actually wrong. Labels from block b1 should be headers.
        assert(layout.inEdges == [[], [], [(BasicEdgeType.ATTRIBUTE, 0), (BasicEdgeType.ATTRIBUTE, 1)]])
        assert(layout.outEdges == [[(BasicEdgeType.ATTRIBUTE, 2)], [(BasicEdgeType.ATTRIBUTE, 2)], []])

