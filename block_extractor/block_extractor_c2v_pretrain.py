import os
from itertools import product
import numpy as np
from type.cell.cell_type_pmf import CellTypePMF
from utils.psl_utils import *
from block_extractor.block_extractor import BlockExtractor
from block_extractor.block_extractor_v2 import BlockExtractorV2
from type.block.simple_block import SimpleBlock
from type.block.block_type_pmf import BlockTypePMF
from type.block.function_block_type import FunctionBlockType
from cell_classifier.c2v_cell_classifier import C2VCellClassifier
from typing import List
from reader.sheet import Sheet
import pandas as pd

class BlockExtractorC2VPretrain(BlockExtractor):

    def __init__(self, model_file, config):
        self.c2v = C2VCellClassifier(model_file, config)
        self.bev2 = BlockExtractorV2()

    def extract_blocks(self, sheet: Sheet, tags: 'np.array[CellTypePMF]') -> List[SimpleBlock]:

        embs = sheet.meta['embeddings']

        r, c = sheet.values.shape

        new_tags = self.c2v.classify_cells(sheet)

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
