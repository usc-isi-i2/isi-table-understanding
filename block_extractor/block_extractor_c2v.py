import os
from itertools import product
import numpy as np
from joblib import dump, load
from type.cell.function_cell_type import FunctionCellType
from type.cell.cell_type_pmf import CellTypePMF
from utils.psl_utils import *
from block_extractor.block_extractor import BlockExtractor
from block_extractor.block_extractor_v2 import BlockExtractorV2
from type.block.simple_block import SimpleBlock
from type.block.block_type_pmf import BlockTypePMF
from type.block.function_block_type import FunctionBlockType
from typing import List
from reader.sheet import Sheet
import pandas as pd

class BlockExtractorC2V(BlockExtractor):

    def __init__(self, model_file):
        self.model = load(model_file)
        self.bev2 = BlockExtractorV2()

    def convert2cell(self, res, r, c):

        pred = np.empty((r, c), dtype=CellTypePMF)

        idx = 0

        for i in range(r):
            for j in range(c):
                t_id = res[idx]
                t_l = FunctionBlockType.id2str[t_id]

                cell_class_dict = {
                    FunctionCellType.inverse_dict[t_l]: 1.0
                }
                pred[i][j] = CellTypePMF(cell_class_dict)

                idx += 1

        return pred

    def extract_blocks(self, sheet: Sheet, tags: 'np.array[CellTypePMF]') -> List[SimpleBlock]:

        embs = sheet.meta['embeddings']

        r, c = sheet.values.shape

        feat = [embs[i][j] for i in range(r) for j in range(c)]

        result = self.model.predict(feat)

        new_tags = self.convert2cell(result, r, c)

        row_blocks = self.bev2.merge_sheet_left_to_right(sheet, new_tags)

        maximal_blocks = self.bev2.merge_sheet_top_to_bottom(row_blocks)

        blocks = []

        for typ, blk in maximal_blocks:

            lab = typ.str()

            pmf = BlockTypePMF({FunctionBlockType.inverse_dict[lab]: 1.0})

            blocks.append(SimpleBlock(pmf, blk.left_col, blk.right_col, blk.top_row, blk.bottom_row))

        return blocks

    def extract_blocks_all_tables(self, sheets, tags):

        return [self.extract_blocks(sheets[i], None if tags is None else tags[i]) for i in range(len(sheets))]
