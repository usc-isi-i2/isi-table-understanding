import unittest
import numpy as np
from cell_classifier.example_cell_classifier import ExampleCellClassifier
from type.cell.cell_type_pmf import CellTypePMF
from reader.sheet import Sheet
from type.cell import cell_type


class TestExampleClassifier(unittest.TestCase):
    def testExampleClassificationForSimpleTableWithTwoColumns(self):

        example = ExampleCellClassifier()
        values = np.array([['date', 'value'], ['2001', '10.0'], ['2002', '11.0'], ['2003', '12.0']])
        tags = example.classify_cells(Sheet(values, None))

        print(tags)

        expected_tags = np.array([
                                    [CellTypePMF({cell_type.EMPTY: 1}), CellTypePMF({cell_type.EMPTY: 1})],
                                    [CellTypePMF({cell_type.EMPTY: 1}), CellTypePMF({cell_type.EMPTY: 1})],
                                    [CellTypePMF({cell_type.EMPTY: 1}), CellTypePMF({cell_type.EMPTY: 1})],
                                    [CellTypePMF({cell_type.EMPTY: 1}), CellTypePMF({cell_type.EMPTY: 1})]
                                ])

        assert np.array_equal(tags, expected_tags)
