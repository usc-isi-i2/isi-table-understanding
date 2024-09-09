
import unittest
from block_extractor.block_post_processor import split_7_shape

from type.block.simple_block import SimpleBlock
from type.block.basic_block_type import BasicBlockType
from type.block.block_type_pmf import BlockTypePMF

class BlockPostProcessorTest(unittest.TestCase):
    def testSplit7Shape(self):
        bpmf = BlockTypePMF({BasicBlockType.ATTRIBUTE: 1})
        b1 = SimpleBlock(bpmf, 0, 1, 0, 0)
        b2 = SimpleBlock(bpmf, 2, 3, 0, 0)
        b3 = SimpleBlock(bpmf, 0, 0, 1, 1)
        b4 = SimpleBlock(bpmf, 1, 2, 1, 1)
        b5 = SimpleBlock(bpmf, 3, 3, 1, 2)
        b6 = SimpleBlock(bpmf, 0, 2, 2, 2)
        b7 = SimpleBlock(bpmf, 4, 5, 1, 1)

        a, b, c = split_7_shape(b1, b6)
        print(a, b, c)



##########################
# b1 b1 b2 b2
# b3 b4 b4 b5 b7 b7
# b6 b6 b6 b5
#
#
#
#
#