import os
import numpy as np
from layout_detector.psl.featurizer import Featurize
from utils.psl_utils import *
from layout_detector.layout_detector import LayoutDetector
from type.layout.layout_graph import LayoutGraph
from type.block.simple_block import SimpleBlock
from type.layout.basic_edge_type import BasicEdgeType
from reader.sheet import Sheet
from typing import List

class LayoutDetectorPSL(LayoutDetector):

    def __init__(self, **args):
        psl_name_file = args['layout_detector_name']

        self.psl_pred_file = args['predicate_file']

        self.psl_rule_file = args['rule_file']

        self.psl_eval_data_path = args['eval_path']

        if not os.path.exists(self.psl_eval_data_path):

            os.makedirs(self.psl_eval_data_path, exist_ok=True)

        self.model = Model(psl_name_file)

        self.feat = Featurize()

    def __read_type_df(self, df):

        type_dic = {}

        for (_, idx, bi, bj, an, val) in df.itertuples(name=None):

            an_type = BasicEdgeType.str_to_edge_type[an]

            val = float(val)

            if (idx, bi, bj) not in type_dic:

                type_dic[(idx, bi, bj)] = (an_type, val)

            elif val > type_dic[(idx, bi, bj)][1]:

                type_dic[(idx, bi, bj)] = (an_type, val)

        return type_dic


    def __predict_wrapper(self, pred, blocks):

        type_dic = self.__read_type_df(pred)

        layout_graphs = [LayoutGraph(blk) for blk in blocks]

        for k, v in type_dic.items():

            layout_graphs[k[0]].add_edge(v[0], k[1], k[2])

        return layout_graphs

    def generate_feats(self, blocks):

        self.feat.featurize(blocks, None, self.psl_pred_file, self.psl_eval_data_path)

        get_predicates(self.model, self.psl_pred_file)

        add_data(self.model, self.psl_eval_data_path)

        get_rules(self.model, self.psl_rule_file)

        results = self.model.infer()

        pred = results[self.model.get_predicate(self.feat.objective)]

        return pred

    def detect_layout(self, sheet: Sheet, tags: 'np.array[CellTypePMF]', blocks: List[SimpleBlock]):

        pred = self.generate_feats([blocks])

        layout_graphs = self.__predict_wrapper(pred, [blocks])

        return layout_graphs[0]

    def detect_layout_all_tables(self, sheet, tags, blocks):

        pred = self.generate_feats(blocks)

        layout_graphs = self.__predict_wrapper(pred, blocks)

        return layout_graphs

    def reset(self):
        self.__init__()
