import unittest
import numpy as np
from type.cell.cell_type_pmf import CellTypePMF
from type.block.simple_block import SimpleBlock
from type.layout.layout_graph import LayoutGraph
from layout_detector.crf.estimator import CRFLayoutEstimator
from type.cell.cell_type_pmf import CellTypePMF
from type.block.simple_block import SimpleBlock
from layout_detector.example_layout_detector import ExampleLayoutDetector
from reader.sheet import Sheet
from type.cell import cell_type

from type.block.block_type_pmf import BlockTypePMF
from type.block import block_type
from type.layout import edge_type


class TestCRFEstimator(unittest.TestCase):

    def testCRFEstimator(self):

        ATTRIBUTE = BlockTypePMF({block_type.ATTRIBUTE: 1.0})
        VALUE = BlockTypePMF({block_type.VALUE: 1.0})

        # Table 1
        sheet1 = np.array([['date', 'value'], ['2001', '10.0'], ['2002', '11.0'], ['2003', '12.0']])
        sheet1 = Sheet(sheet1, None)
        tags1 = np.array([[CellTypePMF({cell_type.META: 1}), CellTypePMF({cell_type.META: 1})],
                          [CellTypePMF({cell_type.DATE: 1}), CellTypePMF({cell_type.DATA: 1})],
                          [CellTypePMF({cell_type.DATE: 1}), CellTypePMF({cell_type.DATA: 1})],
                          [CellTypePMF({cell_type.DATE: 1}), CellTypePMF({cell_type.DATA: 1})]])

        b1_1 = SimpleBlock(ATTRIBUTE, 0, 1, 0, 0)
        b1_2 = SimpleBlock(ATTRIBUTE, 0, 0, 1, 3)  # Todo: This is not correct
        b1_3 = SimpleBlock(VALUE, 1, 1, 1, 3)
        blocks1 = [b1_1, b1_2, b1_3]

        # Table 2
        sheet2 = np.array([['date', 'value'], ['10.0', '2001'], ['11.0', '2002'], ['12.0', '2003']])
        tags2 = np.array([[CellTypePMF({cell_type.META: 1}), CellTypePMF({cell_type.META: 1})],
                          [CellTypePMF({cell_type.DATA: 1}), CellTypePMF({cell_type.DATE: 1})],
                          [CellTypePMF({cell_type.DATA: 1}), CellTypePMF({cell_type.DATE: 1})],
                          [CellTypePMF({cell_type.DATA: 1}), CellTypePMF({cell_type.DATE: 1})]])

        b2_1 = SimpleBlock(ATTRIBUTE, 0, 1, 0, 0)
        b2_2 = SimpleBlock(VALUE, 0, 0, 1, 3)
        b2_3 = SimpleBlock(ATTRIBUTE, 1, 1, 1, 3)
        blocks2 = [b2_1, b2_2, b2_3]

        layoutGraph1 = LayoutGraph(blocks1)
        layoutGraph1.add_edge(edge_type.HEADER, 0, 1)
        layoutGraph1.add_edge(edge_type.HEADER, 0, 2)
        layoutGraph1.add_edge(edge_type.ATTRIBUTE, 1, 2)

        layoutGraph2 = LayoutGraph(blocks1)
        layoutGraph2.add_edge(edge_type.HEADER, 0, 1)
        layoutGraph2.add_edge(edge_type.HEADER, 0, 2)
        layoutGraph2.add_edge(edge_type.ATTRIBUTE, 2, 1)


        estimator = CRFLayoutEstimator()
        estimator.set_input([sheet1, sheet2, sheet1, sheet2],
                                                [tags1, tags2, tags1, tags2],
                                                [blocks1, blocks2, blocks1, blocks2],
                                                [layoutGraph1, layoutGraph2, layoutGraph1, layoutGraph2])


        crf_layout_detector = estimator.fit_crf()

