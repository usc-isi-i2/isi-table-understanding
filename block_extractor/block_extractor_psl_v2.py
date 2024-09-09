import os
import numpy as np
from type.cell.function_cell_type import FunctionCellType
from type.cell.cell_type_pmf import CellTypePMF
from block_extractor.psl.features_v2 import Block2FeatV2
from utils.psl_utils import *
from block_extractor.block_extractor import BlockExtractor
from block_extractor.block_extractor_c2v import BlockExtractorC2V
from type.block.simple_block import SimpleBlock
from type.block.block_type_pmf import BlockTypePMF
from type.block.function_block_type import FunctionBlockType
from typing import List
from reader.sheet import Sheet
import pandas as pd

class BlockExtractorPSLV2(BlockExtractor):

    def __init__(self, **args):
        self.c2v_model = BlockExtractorC2V(args["model_file"])

        psl_name_file = args['block_extractor_name']

        self.psl_pred_file = args['predicate_file']

        self.psl_rule_file = args['rule_file']

        self.psl_eval_data_path = args['eval_path']

        if not os.path.exists(self.psl_eval_data_path):

            os.makedirs(self.psl_eval_data_path, exist_ok=True)

        self.model = Model(psl_name_file)

        self.feat = Block2FeatV2(args)

    def convert2cell(self, blocks, r, c):

        pred = np.empty((r, c), dtype=CellTypePMF)

        for block in blocks:
            lx, ly = block.top_row, block.left_col
            rx, ry = block.bottom_row, block.right_col
            lab = block.block_type.get_best_type().str()

            for i in range(lx, rx + 1):
                for j in range(ly, ry + 1):

                    cell_class_dict = {
                        FunctionCellType.inverse_dict[lab]: 1.0
                    }
                    pred[i][j] = CellTypePMF(cell_class_dict)

        return pred

    def select_blks(self, labels, mr, mc):

        blocks = []

        for blk in labels.keys():

            (lx, ly, rx, ry) = blk
            typ = labels[blk][0]

            temp = SimpleBlock(BlockTypePMF(
                        {FunctionBlockType.inverse_dict[typ]: 1.0}
                        ),
                    ly, ry, lx, rx)

            blocks.append(temp)

        return blocks

    def __read_label_df(self, df):

        block_dic = {}

        for (_, idx, li, lj, ri, rj, an, val) in df.itertuples(name=None):

            if idx not in block_dic:
                block_dic[idx] = {}

            if (li, lj, ri, rj) not in block_dic[idx]:

                block_dic[idx][(li, lj, ri, rj)] = (an, float(val))

            elif block_dic[idx][(li, lj, ri, rj)][1] < float(val):

                block_dic[idx][(li, lj, ri, rj)] = (an, float(val))

        return block_dic

    def __predict_wrapper(self, lab_pred, sheets):

        label_dic = self.__read_label_df(lab_pred)

        preds = []

        for i in range(len(sheets)):

            mr, mc = sheets[i].values.shape

            pred = self.select_blks(label_dic[i], mr, mc)

            preds.append(pred)

        return preds

    def generate_feats(self, sheets, tags, c2v_celltypes=None):

        self.feat.write_feats(sheets, tags, None, c2v_celltypes,
                              self.psl_pred_file, self.psl_eval_data_path)

        get_predicates(self.model, self.psl_pred_file)

        add_data(self.model, self.psl_eval_data_path)

        get_rules(self.model, self.psl_rule_file)

        results = self.model.infer()

        label_pred = results[self.model.get_predicate(self.feat.pred_name)]

        return label_pred

    def postprocessv2(self, blocks, sheet):
        pos_dic = {}
        for blk in blocks:
            lx = blk.top_row
            if lx not in pos_dic:
                pos_dic[lx] = []
            pos_dic[lx].append(blk)
        new_dic = {}
        new_pos_dic = {}
        for lx in pos_dic:
            blk_list = sorted(pos_dic[lx], key=lambda x:x.left_col)
            temp_blk = None
            new_dic[lx] = []
            for i in range(len(blk_list)):
                if temp_blk is None:
                    temp_blk = blk_list[i]
                elif ((temp_blk.right_col + 1) == blk_list[i].left_col) and (temp_blk.top_row == blk_list[i].top_row) and (temp_blk.bottom_row == blk_list[i].bottom_row):
                    if temp_blk.block_type.get_best_type().str() == blk_list[i].block_type.get_best_type().str():
                        new_blk = SimpleBlock(
                                temp_blk.block_type,
                                temp_blk.get_left_col(), blk_list[i].get_right_col(),
                                temp_blk.get_top_row(), temp_blk.get_bottom_row())
                        temp_blk = new_blk
                    else:
                        new_dic[lx].append(temp_blk)
                        temp_blk = blk_list[i]
                else:
                    new_dic[lx].append(temp_blk)
                    temp_blk = blk_list[i]

            if temp_blk is not None:
                new_dic[lx].append(temp_blk)

        for k in new_dic.keys():
            for blk in new_dic[k]:
                if blk.left_col not in new_pos_dic:
                    new_pos_dic[blk.left_col] = []
                new_pos_dic[blk.left_col].append(blk)

        ret_list = []
        for k in new_pos_dic:
            blk_list = sorted(new_pos_dic[k], key=lambda x:x.top_row)
            temp_blk = None
            for i in range(len(blk_list)):
                if temp_blk is None:
                    temp_blk = blk_list[i]
                else:
                    if (temp_blk.bottom_row + 1 == blk_list[i].top_row) and (temp_blk.left_col == blk_list[i].left_col) and (temp_blk.right_col == blk_list[i].right_col) and (temp_blk.block_type.get_best_type().str() == blk_list[i].block_type.get_best_type().str()):

                        new_blk = SimpleBlock(
                                    temp_blk.block_type,
                                    temp_blk.get_left_col(), temp_blk.get_right_col(),
                                    temp_blk.get_top_row(), blk_list[i].get_bottom_row())
                        temp_blk = new_blk
                    else:
                        ret_list.append(temp_blk)
                        temp_blk = blk_list[i]
            if temp_blk is not None:
                ret_list.append(temp_blk)

        return ret_list

    def postprocessv2_recursive(self, blocks, sheet):
        while True:
            ret_blocks = self.postprocessv2(blocks, sheet)
            if len(ret_blocks) == len(blocks):
                return ret_blocks
            blocks = ret_blocks

    def extract_blocks(self, sheet: Sheet, tags: 'np.array[CellTypePMF]') -> List[SimpleBlock]:

        c2v_tags = self.c2v_model.extract_blocks(sheet, None)

        r, c = sheet.values.shape

        c2v_celltypes = self.convert2cell(c2v_tags, r, c)

        lab_pred = self.generate_feats([sheet], [tags], [c2v_celltypes])

        all_blocks = self.__predict_wrapper(lab_pred, [sheet])

        assert len(all_blocks) == 1

        return self.postprocessv2_recursive(all_blocks[0], sheet)

    def reset(self):
        self.__init__()
