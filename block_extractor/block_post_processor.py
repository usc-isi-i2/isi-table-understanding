from type.cell import cell_type
from type.block.basic_block_type import BasicBlockType
from type.cell.basic_cell_type import BasicCellType
from type.block.block_type_pmf import BlockTypePMF
from typing import List
from type.block.simple_block import SimpleBlock

"""
Use: get_cell_distribution_of_split from block_extractor_decision_tree for an optimized implementation
"""
def get_cell_distribution_of_block(tags: 'np.array[CellTypePMF]', block: SimpleBlock):
    count = dict()
    for i in range(block.get_top_row(), block.get_bottom_row() + 1):
        for j in range(block.get_left_col(), block.get_right_col() + 1):
            tag = tags[i][j].get_best_type()
            if tag not in count:
                count[tag] = 0
            count[tag] += 1

    return count

"""
This is an unoptimized implementation. Improvements can be made in counting the
maximum tag in a block.
"""
def add_basic_type_to_blocks(tags: 'np.array[CellTypePMF]', blocks: List[SimpleBlock]):
    for block in blocks:
        assert block.block_type is None

        count = get_cell_distribution_of_block(tags, block)
        # Find maximum repeated tag in a block
        if BasicCellType.DATA in count and BasicCellType.DATE in count and\
                count[BasicCellType.DATE] > count[BasicCellType.DATA]:
            block.block_type = BlockTypePMF({BasicBlockType.ATTRIBUTE: 1.0})
        elif BasicCellType.DATA in count and BasicCellType.META in count and\
                count[BasicCellType.META] > count[BasicCellType.DATA]:
            block.block_type = BlockTypePMF({BasicBlockType.ATTRIBUTE: 1.0})
        elif BasicCellType.DATA in count:
            block.block_type = BlockTypePMF({BasicBlockType.VALUE: 1.0})
        elif BasicCellType.DATE in count or BasicCellType.META in count:
            block.block_type = BlockTypePMF({BasicBlockType.ATTRIBUTE: 1.0})
        else:
            block.block_type = BlockTypePMF({BasicBlockType.EMPTY: 1.0})


def split_7_shape(block_a: SimpleBlock, block_b: SimpleBlock):
    if not block_a.is_adjacent(block_b):
        return block_a, None, block_b
    b1, b2, b3 = None, None, None

    if block_a.right_col == block_b.right_col and block_a.left_col != block_b.left_col:
        if block_b.is_above(block_a):
            block_a, block_b = block_b, block_a

        b1 = SimpleBlock(block_a.block_type, block_a.left_col, block_b.left_col-1,
                         block_a.top_row, block_a.bottom_row)
        b2 = SimpleBlock(BlockTypePMF({BasicBlockType.HEADER: 1.0}), block_b.left_col, block_b.right_col,
                         block_a.top_row, block_a.bottom_row)
        b3 = block_b

    if block_a.left_col == block_b.left_col and block_a.right_col != block_b.right_col:
        if block_b.is_above(block_a):
            block_a, block_b = block_b, block_a

        b1 = SimpleBlock(block_a.block_type, block_b.right_col + 1, block_a.right_col,
                         block_a.top_row, block_a.bottom_row)
        b2 = SimpleBlock(BlockTypePMF({BasicBlockType.HEADER: 1.0}), block_b.left_col, block_b.right_col,
                         block_a.top_row, block_a.bottom_row)
        b3 = block_b

    if block_a.top_row == block_b.top_row and block_a.bottom_row != block_b.bottom_row:
        if block_a.bottom_row > block_b.bottom_row:
            block_a, block_b = block_b, block_a

        b1 = block_a
        b2 = SimpleBlock(BlockTypePMF({BasicBlockType.HEADER: 1.0}), block_b.left_col, block_b.right_col,
                         block_a.top_row, block_a.bottom_row)
        b3 = SimpleBlock(block_b.block_type, block_b.left_col, block_b.right_col,
                         block_a.bottom_row + 1, block_b.bottom_row)

    return b1, b2, b3


def split_header_blocks_from_attribute_blocks(blocks: List[SimpleBlock]):
    ## Find 2 attribute blocks which make 7 or mirror of 7 - shape and then split them into 3
    # Can this be implemented better?
    splitting = True
    while splitting:
        splitting = False
        for block_a in blocks:
            for block_b in blocks:
                if block_a != block_b and block_a.block_type.get_best_type() == BasicBlockType.ATTRIBUTE and\
                        block_b.block_type.get_best_type() == BasicBlockType.ATTRIBUTE:
                    b1, b2, b3 = split_7_shape(block_a, block_b)
                    if b2 is not None and b2.get_height() <= 3:
                        print("Removing blocks {}, {}".format(block_a, block_b))
                        blocks.remove(block_a)
                        blocks.remove(block_b)
                        print("Inserting blocks {}, {}, {}".format(b1, b2, b3))
                        blocks.extend([b1, b2, b3])

                        splitting = True
                if splitting:
                    break
            if splitting:
                break


def find_global_attribute_blocks(blocks: List[SimpleBlock]):
    if len(blocks) == 1:
        return
    ## If block is above every other block
    ## and not aligned with the block below it : it is a global attribute block
    for block_a in blocks:
        top_block = True
        for block_b in blocks:
            if block_a != block_b and not block_a.is_above(block_b):
                top_block = False
                break

        if top_block:
            aligned_block_found = False
            for block_c in blocks:
                if block_c.are_blocks_vertical(block_a) and block_c.are_blocks_within_x_row_or_column(3, block_a):
                    aligned_block_found = True
                    break
            if not aligned_block_found:
                block_a.block_type = BlockTypePMF({BasicBlockType.GLOBAL_ATTRIBUTE: 1.0})
            break  # No other block can be at the top

    ## If block is below every other block
    ## and not aligned with the block above it : it is a global attribute block
    for block_a in blocks:
        bottom_block = True
        for block_b in blocks:
            if block_a != block_b and not block_a.is_below(block_b):
                bottom_block = False
                break

        if bottom_block:
            aligned_block_found = False
            for block_c in blocks:
                if block_c.are_blocks_vertical(block_a) and\
                        block_c.are_blocks_within_x_row_or_column(3, block_a):
                    aligned_block_found = True
                    break
            if not aligned_block_found:
                block_a.block_type = BlockTypePMF({BasicBlockType.GLOBAL_ATTRIBUTE: 1.0})
            break  # No other block can be at the bottom


def postprocess(tags: 'np.array[CellTypePMF]', blocks: List[SimpleBlock]):
    add_basic_type_to_blocks(tags, blocks)
    split_header_blocks_from_attribute_blocks(blocks)
    for block in blocks:
        print(block)
    find_global_attribute_blocks(blocks)

