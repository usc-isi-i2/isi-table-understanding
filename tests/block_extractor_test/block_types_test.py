import unittest
from type.block.block_type import BlockType


class TestNewBlockTypes(unittest.TestCase):
    def testNewBlockTypes(self):
        EMPTY = BlockType("empty_block", 100)

        assert EMPTY.id() == 100
        assert EMPTY.str() == "empty_block"
