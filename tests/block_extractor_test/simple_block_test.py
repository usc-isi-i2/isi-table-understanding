import unittest
from type.block.simple_block import SimpleBlock
from type.block.basic_block_type import BasicBlockType


class TestSimpleBlock(unittest.TestCase):
    def testSimpleBlockFunctions(self):

        b1 = SimpleBlock(BasicBlockType.HEADER, 0, 1, 0, 0)
        b2 = SimpleBlock(BasicBlockType.ATTRIBUTE, 0, 0, 1, 3)
        b3 = SimpleBlock(BasicBlockType.VALUE, 1, 1, 1, 3)
        b4 = SimpleBlock(BasicBlockType.VALUE, 0, 1, 4, 4)
        b5 = SimpleBlock(BasicBlockType.VALUE, 2, 3, 1, 1)
        b6 = SimpleBlock(BasicBlockType.EMPTY, 0, 1, 1, 1)

        assert b1.is_adjacent(b2)
        assert b2.is_adjacent(b1)
        assert b2.is_adjacent(b3)
        assert b3.is_adjacent(b2)
        assert b1.is_adjacent(b3)
        assert b3.is_adjacent(b1)
        assert b1.is_above(b6)

        assert not b2.is_above(b3)
        assert not b3.is_above(b2)
        assert not b1.is_adjacent(b4)
        assert not b4.is_adjacent(b1)
        assert not b1.is_adjacent(b5)
        assert not b5.is_adjacent(b1)

