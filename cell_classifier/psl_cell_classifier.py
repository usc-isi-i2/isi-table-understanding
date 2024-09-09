from cell_classifier.cell_classifier import CellClassifier
from cell_classifier.c2v_cell_classifier_v2 import C2VCellClassifierV2
from cell_classifier.mlp_cell_classifier_v2 import MLPCellClassifierV2
import numpy as np
from type.cell.cell_type_pmf import CellTypePMF
from type.cell.semantic_cell_type import SemanticCellType
from reader.sheet import Sheet
from typing import List
from cell_classifier.psl.features import Cell2Feat
from utils.psl_utils import *

class PSLCellClassifier(CellClassifier):
    def __init__(self, **args):

        self.c2v_model = C2VCellClassifierV2(args["model_file"])

        psl_name_file = args['cell_classifier_name']

        self.psl_pred_file = args['predicate_file']

        # Path to rules
        self.psl_rule_file = args['rule_file']

        self.psl_eval_data_path = args['eval_path']
        print(self.psl_rule_file)

        if not os.path.exists(self.psl_eval_data_path):
            os.makedirs(self.psl_eval_data_path, exist_ok=True)

        self.model = Model(psl_name_file)

        self.feat = Cell2Feat()

    def __read_cell_df(self, df):
        type_dic = {}

        # Read the output df from the PSL model
        for (_, i, rid, cid, an, val) in df.itertuples(name=None):

            if (i, rid, cid) not in type_dic:

                type_dic[(i, rid, cid)] = {}

            type_dic[(i, rid, cid)][an] = val

        return type_dic

    def __predict_wrapper(self, prediction, sheets):

        type_dic = self.__read_cell_df(prediction)

        if isinstance(sheets, Sheet):

            sheets = [sheets]

        preds = []

        for idx, sheet in enumerate(sheets):

            r, c = sheet.values.shape

            pred = np.empty((r, c), dtype=CellTypePMF)

            for i in range(r):

                for j in range(c):

                    type_class = {SemanticCellType.inverse_dict[k]: v
                                  for k, v in type_dic[(idx, i, j)].items()}

                    pred[i][j] = CellTypePMF(type_class)

            preds.append(pred)

        return preds

    def write_feat_obj(self, sheets, tags):

        self.feat.write_feats(sheets, None, tags, self.psl_pred_file, self.psl_eval_data_path)

        get_predicates(self.model, self.psl_pred_file)

        add_data(self.model, self.psl_eval_data_path)

        get_rules(self.model, self.psl_rule_file)

        results = self.model.infer()

        return results

    def classify_cells(self, sheet: Sheet) -> 'np.ndarray[CellTypePMF]':

        c2v_tags = self.c2v_model.classify_cells_all_tables([sheet])

        c2v_tags = [[[_.get_best_type().str() for _ in row] for row in tags]
                    for tags in c2v_tags]

        results = self.write_feat_obj([sheet], c2v_tags)

        tags = self.__predict_wrapper(results[self.model.get_predicate(self.feat.pred_name)],
                                      [sheet])

        assert len(tags) == 1

        return tags[0]

    def classify_cells_all_tables(self, sheets):

        c2v_tags = self.c2v_model.classify_cells_all_tables(sheets)

        c2v_tags = [[[_.get_best_type().str() for _ in row] for row in tags]
                    for tags in c2v_tags]

        results = self.write_feat_obj(sheets, c2v_tags)

        tags = self.__predict_wrapper(results[self.model.get_predicate(self.feat.pred_name)],
                                      sheets)
        return tags

    def reset(self):
        self.__init__()
