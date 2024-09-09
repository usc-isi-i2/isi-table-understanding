import numpy as np
from block_extractor.block_extractor import BlockExtractor
from type.block.simple_block import SimpleBlock
from typing import List

# Region Algebra : http://www.cs.cmu.edu/~rcm/papers/thesis/ch4.pdf
"""
Naive implementation of a block extractor.
First iterate row by row and merge consecutive cells in the same row with the same tag.
Next iterate row by row and group two blocks which have the same start and end positions and the same tag.

This procedure is described in more detail in "Table Recognition in Spreadsheets via a Graph Representation"\
under Definition 4. 
"""


@DeprecationWarning
class SimpleBlockExtractor(BlockExtractor):
    def merge_row_left_to_right(self, row_id, row, tags):
        curr_block_start = 0
        row_blocks = []
        for i in range(1, len(row)):
            if tags[i] != tags[i-1]:
                row_blocks.append(SimpleBlock(tags[i-1].get_best_type(), curr_block_start, i - 1, row_id, row_id))
                curr_block_start = i

        cols = len(row)
        row_blocks.append(SimpleBlock(tags[cols-1].get_best_type(), curr_block_start, cols - 1, row_id, row_id))
        return row_blocks

    def merge_sheet_left_to_right(self, sheet, tags) -> List:
        row_blocks = [self.merge_row_left_to_right(row_id, row, row_tags) for row_id, (row, row_tags) in enumerate(zip(sheet, tags))]
        return row_blocks

    def merge_sheet_top_to_bottom(self, row_blocks: List) -> List:
        blocks = []
        up = row_blocks[0]  # Blocks which might be merged with rows below
        for i in range(1, len(row_blocks)):
            down = row_blocks[i]

            j, k = 0, 0
            new_up = []
            # TODO: Verify correctness
            # TODO: Handle empty cells
            while j < len(up) and k < len(down):
                if up[j].get_left_col() == down[k].get_left_col() and up[j].get_right_col() == down[k].get_right_col()\
                        and up[j].get_block_type() == down[k].get_block_type():
                    # Merge two blocks
                    new_up.append(SimpleBlock(up[j].get_block_type(), up[j].get_left_col(), up[j].get_right_col(),
                                              up[j].get_top_row(), down[k].get_bottom_row()))
                    j += 1
                    k += 1

                elif up[j].get_right_col() < down[k].get_right_col():
                    blocks.append(up[j])
                    j += 1

                elif down[k].get_right_col() < up[j].get_right_col():
                    new_up.append(down[k])
                    k += 1

                elif up[j].get_right_col() == down[k].get_right_col():
                    blocks.append(up[j])
                    new_up.append(down[k])
                    j += 1
                    k += 1
            up = new_up

        blocks.extend(up)  # Add whatevers left
        return blocks

    def extract_blocks(self, sheet: np.array, tags: np.array) -> List[SimpleBlock]:
        row_blocks = self.merge_sheet_left_to_right(sheet, tags)
        blocks = self.merge_sheet_top_to_bottom(row_blocks)
        return blocks