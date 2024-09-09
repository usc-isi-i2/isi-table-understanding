import os
import sys
from itertools import product
import numpy as np
import pyexcel as pyx
from reader.sheet import Sheet
from type.block.function_block_type import FunctionBlockType
from type.cell.cell_type_pmf import CellTypePMF
from type.cell.semantic_cell_type import SemanticCellType
from type.block.simple_block import SimpleBlock
from block_extractor.block_extractor_mcmc_v2 import BlockExtractorMCMC
from block_extractor.block_extractor_hac import BlockExtractorHAC, DistFuncs
from cell_classifier.psl.features import *
from sklearn.metrics.pairwise import paired_distances
from scipy.spatial import distance
import pickle

class Block2FeatV2:
    def __init__(self, args):
        self.pred_name = "label"

        self.predvars = 6

        self.tags = ["firstrow",
                     "singlecolbefore", "singlecolafter",
                     "neighbor", "cell2vec",
                     "validblock", "datatype",
                     ]
        self.tagvars = [3, 2, 2, 2, 6, 5, 6]
        self.tag_dic = {_: set() for _ in self.tags}
        self.cell2vec = {}
        self.datatype = {}
        self.args = args

    def write_predicates(self, pred_path):
        str_list = []

        for i in range(len(self.tags)):
            str_list.append("{}\t{}\t{}".format(self.tags[i], self.tagvars[i], "closed"))

        str_list.append("{}\t{}\t{}".format(self.pred_name, self.predvars, "open"))

        if pred_path is None:
            return

        with open(pred_path, "w+") as f:

            f.write("\n".join(str_list))

    def generate_blocks(self, sheet, c2vtypes, celltypes):
        if self.args["method"] == "mcmc":
            bev2 = BlockExtractorMCMC(beta=self.args["beta"],
                                      lmd=self.args["lmd"],
                                      num_process=self.args["num_process"],
                                      N=self.args["num_tree"])
            blks = bev2.extract_blocks(sheet, celltypes)
        else:
            with open(self.args["weights_path"], "rb") as f:
                ct_weights = pickle.load(f)
            with open(self.args["metric_path"], "rb") as f:
                learner = pickle.load(f)

            (r, c) = sheet.values.shape
            ori_emb = np.array(sheet.meta["embeddings"]).reshape((r*c, -1))
            new_emb = learner.transform(ori_emb).reshape((r, c, -1))
            m_fun = distance.euclidean
            s_fun = lambda x, y: distance.cdist(x, y, "euclidean")
            c_fun = lambda x, y: paired_distances(x, y, metric="euclidean")
            dist_func = DistFuncs(new_emb, "avg",
                                  c_fun, m_fun, s_fun)

            bev2 = BlockExtractorHAC(self.args["row_perc"],
                                     self.args["col_perc"],
                                     ct_weights, 500)
            blks = bev2.extract_blocks(sheet, celltypes, dist_func)
        return blks

    def serialize_blocks_truth_targets(self, sheets, blocks, tags, celltypes, tid=0):
        target_strs, truth_strs  = {}, {}

        if isinstance(sheets, list):

            for i, sheet in enumerate(sheets):

                t_blocks = None if blocks is None else blocks[i]

                temp_target, temp_truth = self.serialize_blocks_truth_targets(sheet, t_blocks, tags[i], celltypes[i], i)
                #print("generated {} table {}".format(i, sheet.values.shape))

                if len(target_strs) == 0:
                    target_strs = temp_target
                    truth_strs = temp_truth
                else:
                    for k in target_strs:
                        target_strs[k] += temp_target[k]
                        truth_strs[k] += temp_truth[k]

            return target_strs, truth_strs

        max_x, max_y = sheets.values.shape

        block_dic = {}

        if blocks is None:
            maximal_blocks = self.generate_blocks(sheets, tags, celltypes)
        else:
            maximal_blocks = blocks

        temp_dic = set()

        for block in maximal_blocks: #cand_blocks:

            lx, ly = block.get_top_row(), block.get_left_col()
            rx, ry = block.get_bottom_row(), block.get_right_col()
            blk_temp_str = "{}\t{}\t{}\t{}\t{}"
            blk_temp = blk_temp_str.format(tid, lx, ly, rx, ry)

            celltype_cnt = {}
            datatype_cnt = {}

            for li in range(lx, rx + 1):
                for ri in range(ly, ry + 1):
                    temp_dt = celltypes[li][ri].get_best_type().str()
                    if temp_dt not in datatype_cnt:
                        datatype_cnt[temp_dt] = 0
                    datatype_cnt[temp_dt] += 1

                    temp_lab = tags[li][ri].get_best_type().str()
                    if temp_lab not in celltype_cnt:
                        celltype_cnt[temp_lab] = 0
                    celltype_cnt[temp_lab] += 1


            total_cnt = sum(celltype_cnt.values())
            for (k, v) in celltype_cnt.items():
                self.tag_dic["cell2vec"].add("{}\t{}\t{}".format(blk_temp, k, float(v)/total_cnt))
            total_dt_cnt = sum(datatype_cnt.values())
            for (k, v) in datatype_cnt.items():
                self.tag_dic["datatype"].add("{}\t{}\t{}".format(blk_temp, k, float(v)/total_dt_cnt))


            if "label" not in target_strs:
                target_strs["label"] = []
                truth_strs["label"] = []

            for an in FunctionBlockType.inverse_dict.keys():
                target_strs["label"].append("{}\t{}".format(blk_temp, an))
                truth_strs["label"].append("{}\t{}\t{}".format(blk_temp, an, 1.0 / len(FunctionBlockType.inverse_dict)))


        return target_strs, truth_strs

    def write_feats(self, sheets, celltypes, block_annotate, c2v_results=None, pred_path=None, path=None):

        target_str = self.write_objective(sheets, block_annotate, c2v_results, celltypes, path)

        self.generate_pos_feats_all_tables(celltypes, sheets, target_str, path)

        self.write_predicates(pred_path)

    def write_objective(self, sheets, block_annotate, c2v_types, celltypes, path):

        if path is None:
            return

        target_str, truth_str = self.serialize_blocks_truth_targets(sheets, block_annotate, c2v_types, celltypes)

        for k in target_str:
            with open(os.path.join(path, k + "_targets.txt"), "w+") as f:
                f.write("\n".join(target_str[k]))

            if block_annotate is not None:

                with open(os.path.join(path, k + "_truth.txt"), "w+") as f:
                    f.write("\n".join(truth_str[k]))

        return target_str

    def generate_pos_feats_all_tables(self, celltypes, sheets, target_str, path=None):
        for i, sheet in enumerate(sheets):
            temp_dic = self.generate_pos_feats_a_table(celltypes[i], sheet, target_str, i)

        if path is None:
            return

        for k in self.tag_dic:
            with open(os.path.join(path, k + "_obs.txt"), "w+") as f:
                f.write("\n".join(list(self.tag_dic[k])))

    def generate_pos_feats_a_table(self, celltypes, sheet, target_str, sid=0):

        max_x, max_y = celltypes.shape

        first_cols = [-1 for _ in range(max_x)]
        first_rows = [-1 for _ in range(max_y)]
        nonempty_cols = [0 for _ in range(max_x)]
        nonempty_rows = [0 for _ in range(max_y)]

        for i in range(max_x):

            for j in range(max_y):

                temp_true = "{}\t{}\t{}\t{}".format(sid, i, j, 1.0)
                temp_false = "{}\t{}\t{}\t{}".format(sid, i, j, 0.0)

                typ = celltypes[i][j].get_best_type()

                if typ.str() == "empty" or len(sheet.values[i][j].strip()) == 0:

                    continue

                if first_rows[j] == -1:
                    first_rows[j] = i
                    self.tag_dic["firstrow"].add(temp_true)
                elif first_rows[j] != i:
                    self.tag_dic["firstrow"].add(temp_false)

                nonempty_cols[i] += 1
                nonempty_rows[j] += 1

        single_col_before = True
        for i in range(max_x):
            if nonempty_cols[i] / float(max_y) <= 0.3 and nonempty_cols[i] <= 2:
                if single_col_before:
                    self.tag_dic["singlecolbefore"].add("{}\t{}\t{}".format(sid, i, 1.0))
                else:
                    self.tag_dic["singlecolbefore"].add("{}\t{}\t{}".format(sid, i, 0.0))

            else:
                self.tag_dic["singlecolbefore"].add("{}\t{}\t{}".format(sid, i, 0.0))
                single_col_before = False

            if i > 0:
                self.tag_dic["neighbor"].add("{}\t{}\t{}".format(i-1, i, 1.0))

        single_col_after = True
        for i in range(max_x-1, -1, -1):
            if nonempty_cols[i] / float(max_y) <= 0.3 and nonempty_cols[i] <= 2:
                if single_col_after:
                    self.tag_dic["singlecolafter"].add("{}\t{}\t{}".format(sid, i, 1.0))
                else:
                    self.tag_dic["singlecolafter"].add("{}\t{}\t{}".format(sid, i, 0.0))

            else:
                self.tag_dic["singlecolafter"].add("{}\t{}\t{}".format(sid, i, 0.0))
                single_col_after = False

        for j in range(max_y):
            if j > 0:
                self.tag_dic["neighbor"].add("{}\t{}\t{}".format(j-1, j, 1.0))

        for item in target_str["label"]:
            temp_item = "\t".join(item.split("\t")[:-1])
            self.tag_dic["validblock"].add("{}\t{}".format(temp_item, 1.0))
