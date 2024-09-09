#TODO

# Write this first
# then fix simple, then v2 then decision tree

import numpy as np
from block_extractor.block_extractor import BlockExtractor
from type.block.simple_block import SimpleBlock
from typing import List
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from type.block.block_type_pmf import BlockTypePMF
from type.block.basic_block_type import BasicBlockType


class ExampleBlockExtractor(BlockExtractor):
    def extract_blocks(self, sheet: Sheet, tags: 'np.array[CellTypePMF]') -> List[SimpleBlock]:
        blocks = []

        # Probability distribution of block type
        bc = BlockTypePMF(
            {
                BasicBlockType.ATTRIBUTE: 0.9,
                BasicBlockType.HEADER: 0.1,
                # block_type.EMPTY: 0
            }
        )
        
        # bc = BlockTypePMF(
        #     {
        #         BasicBlockType.VALUE: 1.0
        #     }
        # )

        row, col = sheet.values.shape
        new_block = SimpleBlock(bc, 0, col-1, 0, row-1)

        blocks.append(new_block)

        return blocks