from type.block.simple_block import SimpleBlock
from type.layout.basic_edge_type import BasicEdgeType
from type.layout.layout_graph import LayoutGraph
from type.block.function_block_type import FunctionBlockType
from typing import List
from reader.sheet import Sheet
import numpy as np
import os


class Featurize:
    def __init__(self):
        self.single_feats = ["topmost", "leftmost"]
        self.single_feats_vars = [2, 2]
        self.double_feats = ["adjacent", "horizontal", "vertical", "isabove", "isbelow",
                             "atleft"]
        self.double_feats_vars = [3, 3, 3, 3, 3, 3]
        self.typ_feats = ["blocktype"]
        self.typ_feats_vars = [3]

        self.single_feats_func = [self.topmost, self.leftmost]
        self.double_feats_func = [self.adjacent, self.horizontal, self.vertical,
                                  self.is_above, self.is_below, self.at_left]
        self.typ_feats_func = [self.blocktype]
        self.objective = "layout"
        self.objective_var = 4

    def at_left(self, block1, block2):
        if block1.right_col != (block2.left_col + 1):
            return 0
        if block1.bottom_row < block2.top_row:
            return 0
        if block1.top_row > block2.bottom_row:
            return 0
        return 1

    def is_above(self, block1, block2):
        return 1 if block1.is_above(block2) else 0

    def is_below(self, block1, block2):
        return 1 if block1.is_below(block2) else 0

    def adjacent(self, block1, block2):
        return 1 if block1.is_adjacent(block2) else 0

    def horizontal(self, block1, block2):
        if block1.get_top_row() <= block2.get_top_row() and block2.get_bottom_row() <= block1.get_bottom_row():
            return 1
        if block2.get_top_row() <= block1.get_top_row() and block1.get_bottom_row() <= block2.get_bottom_row():
            return 1

        return 1 if block1.are_blocks_horizontal(block2) else 0

    def vertical(self, block1, block2):
        b1_ly, b1_ry = block1.left_col, block1.right_col
        b2_ly, b2_ry = block2.left_col, block2.right_col
        if b2_ly >= b1_ly and b2_ly <= b1_ry:
            return 1
        if b1_ly >= b2_ly and b1_ly <= b2_ry:
            return 1
        return 0

    def blocktype(self, blk, typ):
        return 1 if blk.get_block_type().get_best_type().str() == typ else 0

    def topmost(self, blk):
        return 1 if blk.get_top_row() == 0 else 0

    def leftmost(self, blk):
        return 1 if blk.get_left_col() == 0 else 0

    def get_features(self, blocks, tid=0):
        if isinstance(blocks, list) and len(blocks) > 0 and isinstance(blocks[0], list):

            feats = None

            for i in range(len(blocks)):

                temp_feat = self.get_features(blocks[i], i)

                if feats is None:
                    feats = temp_feat
                else:
                    for k in feats:
                        feats[k] += temp_feat[k]
            return feats

        feats = {}

        for i, func in enumerate(self.single_feats_func):
            temp = ["{}\t{}\t{}".format(tid, bid, func(blk))
                                 for bid, blk in enumerate(blocks)]
            feats[self.single_feats[i]] = temp

        for i, func in enumerate(self.double_feats_func):
            temp = []
            for xi, blki in enumerate(blocks):
                for xj, blkj in enumerate(blocks):
                    if xi == xj:
                        continue
                    temp.append("{}\t{}\t{}\t{}".format(tid, xi, xj, func(blki, blkj)))
            feats[self.double_feats[i]] = temp

        for i, func in enumerate(self.typ_feats_func):
            temp = ["{}\t{}\t{}\t{}".format(tid, bid, typ, func(blk, typ))
                    for bid, blk in enumerate(blocks)
                    for typ in FunctionBlockType.inverse_dict.keys()]

            feats[self.typ_feats[i]] = temp

        return feats

    def write_predicates(self, pred_path):
        str_list = []
        for i, p in enumerate(self.single_feats):
            str_list.append("{}\t{}\t{}".format(p, self.single_feats_vars[i], "closed"))
        for i, p in enumerate(self.double_feats):
            str_list.append("{}\t{}\t{}".format(p, self.double_feats_vars[i], "closed"))
        for i, p in enumerate(self.typ_feats):
            str_list.append("{}\t{}\t{}".format(p, self.typ_feats_vars[i], "closed"))

        str_list.append("{}\t{}\t{}".format(self.objective, self.objective_var, "open"))
        with open(pred_path, "w+") as f:
            f.write("\n".join(str_list))

    def write_feats(self, feat_list, feat_name, path, prefix):
        with open(os.path.join(path, feat_name + prefix), "w+") as f:
            f.write("\n".join(feat_list))

    def featurize(self, blocks, layouttypes, pred_path, data_path):
        feats = self.get_features(blocks)
        for f, vec in feats.items():
            self.write_feats(vec, f, data_path, "_obs.txt")

        targets, truths = self.get_targets_truth(layouttypes, blocks)

        self.write_feats(targets, self.objective, data_path, "_targets.txt")

        if layouttypes is not None:
            self.write_feats(truths, self.objective, data_path, "_truth.txt")
        self.write_predicates(pred_path)

    def get_targets_truth(self, types, blocks, tid=0):

        if isinstance(blocks, list) and len(blocks) > 0 and isinstance(blocks[0], list):
            targets, truths = [], []
            for tid, blk in enumerate(blocks):
                if types is not None:
                    temp_targets, temp_truths = self.get_targets_truth(types[tid], blk, tid)
                else:
                    temp_targets, temp_truths = self.get_targets_truth(types, blk, tid)

                targets += temp_targets
                truths += temp_truths

            return targets, truths

        targets, truths = [], []
        temp_dict = {}

        if types is not None:
            for i, edge in enumerate(types.outEdges):
                for typ in edge:
                    temp_dict[(i, typ[1])] = typ[0].str()

        for i in range(len(blocks)):
            for j in range(len(blocks)):

                if i == j:
                    continue

                for typ in BasicEdgeType.str_to_edge_type.keys():

                    targets.append("{}\t{}\t{}\t{}".format(tid, i, j, typ))

                    if (i, j) in temp_dict and temp_dict[(i, j)] == typ:
                        truths.append("{}\t{}\t{}\t{}\t{}".format(tid, i, j, typ, 1.0))
                    else:
                        truths.append("{}\t{}\t{}\t{}\t{}".format(tid, i, j, typ, 0.0))
        return targets, truths
