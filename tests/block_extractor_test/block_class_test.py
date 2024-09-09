import unittest
from type.block import block_type
from type.block.block_type_pmf import BlockTypePMF


class TestBlockClass(unittest.TestCase):
    def testBlockClass(self):

        block_dict = {
            block_type.EMPTY: 0.9,
            block_type.ATTRIBUTE: 0.1
        }

        bc = BlockTypePMF(block_dict)
        assert bc.get_types() == block_dict
        assert bc.get_best_type() == block_type.EMPTY
