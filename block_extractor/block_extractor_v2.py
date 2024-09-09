import numpy as np
from block_extractor.block_extractor import BlockExtractor
from type.block.simple_block import SimpleBlock
from typing import List
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from type.block.block_type_pmf import BlockTypePMF

class BlockExtractorV2(BlockExtractor):
    def __init__(self):
        pass

    def merge_row_left_to_right(self, row_id, row, tags: List[CellTypePMF]):
        curr_block_start = 0
        row_blocks = []
        for i in range(1, len(row)):
            if tags[i].get_best_type() != tags[i - 1].get_best_type():
                # Appending a tuple (CellType, SimpleBlock), since block type is undetermined at this point
                row_blocks.append((tags[i-1].get_best_type(),
                                   SimpleBlock(None, curr_block_start, i - 1, row_id, row_id)))
                curr_block_start = i

        cols = len(row)
        row_blocks.append((tags[cols-1].get_best_type(),
                          SimpleBlock(None, curr_block_start, cols - 1, row_id, row_id)))
        return row_blocks

    def merge_sheet_left_to_right(self, sheet: Sheet, tags: 'np.array[CellTypePMF]') -> List:
        row_blocks = [self.merge_row_left_to_right(row_id, row, row_tags) for row_id, (row, row_tags) in enumerate(zip(sheet.values, tags))]
        return row_blocks

    def merge_sheet_top_to_bottom(self, row_blocks: List) -> List:
        blocks = []
        up = row_blocks[0]  # Blocks which might be merged with rows below
        for i in range(1, len(row_blocks)):
            down = row_blocks[i]

            j, k = 0, 0
            new_up = []
            while j < len(up) and k < len(down):
                if up[j][1].get_left_col() == down[k][1].get_left_col()\
                        and up[j][1].get_right_col() == down[k][1].get_right_col()\
                        and up[j][0] == down[k][0]:  # Same block type
                    # Merge two blocks
                    new_up.append((
                        up[j][0],
                        SimpleBlock(None, up[j][1].get_left_col(), up[j][1].get_right_col(), up[j][1].get_top_row(),
                                    down[k][1].get_bottom_row())))
                    j += 1
                    k += 1

                elif up[j][1].get_right_col() < down[k][1].get_right_col():
                    blocks.append(up[j])
                    j += 1

                elif down[k][1].get_right_col() < up[j][1].get_right_col():
                    new_up.append(down[k])
                    k += 1

                elif up[j][1].get_right_col() == down[k][1].get_right_col():
                    blocks.append(up[j])
                    new_up.append(down[k])
                    j += 1
                    k += 1
            up = new_up

        blocks.extend(up)  # Add whatevers left
        return blocks

    def extract_blocks(self, sheet: Sheet, tags: 'np.array[CellTypePMF]') -> List[SimpleBlock]:
        row_blocks = self.merge_sheet_left_to_right(sheet, tags)
        blocks = self.merge_sheet_top_to_bottom(row_blocks)

        new_blocks = []
        # Remove empty blocks
        for _type, block in blocks:
            new_blocks.append((_type, block))

        return new_blocks
