import unittest
import numpy as np
from cell_classifier.crf_cell_classifier import CRFCellClassifier
from type.cell.cell_type_pmf import CellTypePMF
from reader.sheet import Sheet
from type.cell.basic_cell_type import BasicCellType

class TestCRFCellClassifier(unittest.TestCase):
    def testCRFClassificationForSimpleTableWithTwoColumns(self):

        crf = CRFCellClassifier()
        values = np.array([['date', 'value'], ['2001', '10.0'], ['2002', '11.0'], ['2003', '12.0']])
        tags = crf.classify_cells(Sheet(values, None))

        expected_tags = np.array([[CellTypePMF({BasicCellType.META: 1}), CellTypePMF({BasicCellType.META: 1})],
                                  [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})],
                                  [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})],
                                  [CellTypePMF({BasicCellType.DATE: 1}), CellTypePMF({BasicCellType.DATA: 1})]])

        assert np.array_equal(tags, expected_tags)
