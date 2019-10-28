from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from typing import List
from type.block.simple_block import SimpleBlock
from type.layout.layout_graph import LayoutGraph
from type.block.basic_block_type import BasicBlockType

import pandas as pd

class DataFrameExtractor:
    def __init__(self, sheet: Sheet, tags: 'np.array[CellTypePMF]', blocks: List[SimpleBlock], layout: LayoutGraph):
        self.sheet = sheet
        self.tags = tags
        self.blocks = blocks
        self.layout = layout

    def get_header(self, sheet: Sheet, header_block: SimpleBlock, idx):
        if header_block is None:
            return "_" + str(idx)

        if header_block.left_col <= idx <= header_block.right_col:
            if header_block.get_height() == 2:
                return str(sheet.values[header_block.top_row][idx]) + "\n" +\
                        str(sheet.values[header_block.bottom_row][idx])
            elif header_block.get_height() == 1:
                return str(sheet.values[header_block.top_row][idx])

        return "_" + str(idx)

    def extract_dataframe(self):
        ## Very simple dataframe extractor
        # Check if only one value block is present
        value_block = None
        value_block_count = 0
        for block in self.blocks:
            if block.get_block_type().get_best_type() == BasicBlockType.VALUE:
                value_block = block
                value_block_count += 1
        if value_block_count != 1:
            return None

        # Find left adjacent attribute block.
        attribute_block = None
        for block in self.blocks:
            if block.right_col + 1 == value_block.left_col and\
                    block.get_block_type().get_best_type() == BasicBlockType.ATTRIBUTE and\
                    abs(block.top_row - value_block.top_row) < 10 and\
                    abs(block.bottom_row - value_block.bottom_row) < 10:
                attribute_block = block
                break

        if attribute_block:
            # Merge two blocks together
            merged_block = SimpleBlock(None,
                                       attribute_block.left_col,
                                       value_block.right_col,
                                       max(attribute_block.top_row, value_block.top_row),
                                       min(attribute_block.bottom_row, value_block.bottom_row)
                                       )
        else:
            merged_block = value_block

        # Find header block
        header_block = None
        for block in self.blocks:
            if block.bottom_row + 1 == value_block.top_row and\
                    block.get_block_type().get_best_type() == BasicBlockType.ATTRIBUTE and\
                    abs(block.left_col - value_block.left_col) < 5 and\
                    abs(block.right_col - value_block.right_col) < 5:
                header_block = block
                break

        if header_block is not None and header_block.get_height() > 2:
            header_block = None

        dataframe = pd.DataFrame()

        for col in range(merged_block.left_col, merged_block.right_col + 1):
            header = self.get_header(self.sheet, header_block, col)
            data = []
            for row in range(merged_block.top_row, merged_block.bottom_row + 1):
                data.append(self.sheet.values[row][col])
            dataframe.loc[:, header] = data

        return dataframe