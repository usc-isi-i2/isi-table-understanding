import numpy as np
from block_extractor.block_extractor import BlockExtractor
from type.block.function_block_type import FunctionBlockType
from type.block.simple_block import SimpleBlock
from typing import List
from joblib import dump, load
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from type.block.block_type_pmf import BlockTypePMF
from type.cell.function_cell_type import FunctionCellType
from block_extractor.block_extractor_v2 import BlockExtractorV2
from block_extractor.crf.featurize import *

class ChainCRFBlockExtractor(BlockExtractor):
    def __init__(self, crf_model_file):
        self.model = load(crf_model_file)

    def postprocess(self, sheet, predictions, r, c):
        bev2 = BlockExtractorV2()

        pred = np.empty((r, c), dtype=CellTypePMF)

        for i in range(r):
            typ = FunctionCellType.id2str[predictions[i]]
            for j in range(c-1, -1, -1):
                if typ != "data":
                    new_typ = typ
                else:
                    is_number = False
                    try:
                        float(sheet.values[i][j].strip())
                        is_number = True
                    except:
                        is_number = False

                    if is_number:
                        if j == c-1 or pred[i][j+1].get_best_type().str() == "data":
                            new_typ = "data"
                        else:
                            new_typ = "attributes"
                    else:
                        new_typ = "attributes"

                cell_class_dict = {
                    FunctionCellType.inverse_dict[new_typ]: 1.0
                }
                pred[i][j] = CellTypePMF(cell_class_dict)


        row_blocks = bev2.merge_sheet_left_to_right(sheet, pred)
        temp_blocks = bev2.merge_sheet_top_to_bottom(row_blocks)

        new_blocks = []
        for l, blk in temp_blocks:
            temp = SimpleBlock(
                    BlockTypePMF({FunctionBlockType.inverse_dict[l.str()]: 1.0}),
                    blk.get_left_col(), blk.get_right_col(),
                    blk.get_top_row(), blk.get_bottom_row())
            new_blocks.append(temp)

        return new_blocks

    def extract_blocks(self, sheet: Sheet, tags: 'np.array[CellTypePMF]') -> List[SimpleBlock]:
        x_test = get_row_feats(sheet)
        predictions = self.model.predict([x_test])[0]
        r, c = sheet.values.shape
        blocks = self.postprocess(sheet, predictions, r, c)
        return blocks

    def extract_blocks_all_tables(self, sheets, tags):
        blocks = [self.extract_blocks(sheet, tags[i]) for i, sheet in enumerate(sheets)]
        return blocks
