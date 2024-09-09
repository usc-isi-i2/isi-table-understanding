import unittest
from type.cell.cell_type import CellType


class TestCellType(unittest.TestCase):
    def testNewBlockTypes(self):
        EMPTY = CellType("empty_block", 100)

        assert EMPTY.id() == 100
        assert EMPTY.str() == "empty_block"
        assert CellType.max_id() == 100
