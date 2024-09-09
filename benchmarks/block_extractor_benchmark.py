from block_extractor.block_extractor import BlockExtractor
import numpy as np
from type.block.simple_block import SimpleBlock

from typing import List


class BlockExtractorBenchmark:
    def __init__(self, sheet: np.array, tags: np.array, block_extractor: BlockExtractor, gold: List[SimpleBlock]):
        self.sheet = sheet
        self.tags = tags
        self.block_extractor = block_extractor
        self.gold = gold

    def get_matching_blocks(self):
        blocks = self.block_extractor.extract_blocks(self.sheet, self.tags)

        for block in blocks:
            print(block)
        print("-----GOLD------")

        for block in self.gold:
            print(block)
        print("---------------")

        # TODO: Compare blocks with gold output
        # and return number of exact matches (dimension, position and type)

        type_mismatch = 0

        matching_blocks = 0
        for block in blocks:
            for block2 in self.gold:
                if block == block2:
                    matching_blocks += 1
                    break
                if block.get_right_col() == block2.get_right_col() and block.get_left_col() == block2.get_left_col() and\
                    block.get_top_row() == block2.get_top_row() and block.get_bottom_row() == block2.get_bottom_row():
                        type_mismatch += 1
                        break


        total_blocks_detected = len(blocks)
        total_blocks_expected = len(self.gold)

        return matching_blocks, type_mismatch, total_blocks_detected, total_blocks_expected
