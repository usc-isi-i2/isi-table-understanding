import unittest
from type.cell.cell_type_pmf import CellTypePMF

class TestCellClass(unittest.TestCase):
    def testCellClass(self):
        cell_class_dict = {
            "_DATA_": 0.51,
            "META": 0.49
        }

        c1 = CellTypePMF(cell_class_dict)

        assert c1.get_best_type() == "_DATA_"
        assert c1.get_types() == cell_class_dict
