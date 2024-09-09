from cell_classifier_psl.psl_utils import *
from block_extractor_psl.features import Block2Feat
from block_extractor_psl.features_v2 import Block2FeatV2
from config_psl import config, get_full_path
from block_extractor.block_extractor_c2v import BlockExtractorC2V
from type.cell.cell_type_pmf import CellTypePMF
from type.cell.function_cell_type import FunctionCellType
from reader.sheet import Sheet
import numpy as np

class PSLWeightLearningBE:

    def __init__(self, k=0, row_thre=0.05, col_thre=0.26, alpha=1., beta=0.5, lmd=5):

        self.c2v_model = BlockExtractorC2V(k)

        self.psl_pred_file = get_full_path(config['block_extractor']['predicate_file'])

        self.psl_rule_file = get_full_path(config['block_extractor']['rule_file'])

        self.psl_learned_rule_file = get_full_path(config['block_extractor']['learned_rule_file'])

        self.psl_learn_data_path = get_full_path(config['block_extractor']['learn_path'])

        if not os.path.exists(self.psl_learn_data_path):
            os.makedirs(self.psl_learn_data_path, exist_ok=True)

        self.model = Model(config['block_extractor']['block_extractor_name'])

        self.feature_version = config['block_extractor']['features']

        self.feat_model = Block2FeatV2(row_thre, col_thre, alpha, beta, lmd)

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


    def learn_weights(self, sheets, tags, c2v_celltypes, blocks):

        c2v_tags = self.c2v_model.extract_blocks_all_tables(sheets, None)

        c2v_celltypes = [self.convert2cell(c2v_tags[i], sheets[i].values.shape[0],
                            sheets[i].values.shape[1]) for i in range(len(sheets))]

        self.feat_model.write_feats(sheets, tags, blocks, c2v_celltypes,
                              self.psl_pred_file, self.psl_learn_data_path)

        get_predicates(self.model, self.psl_pred_file)

        add_data(self.model, self.psl_learn_data_path)

        get_rules(self.model, self.psl_rule_file)

        self.model.learn()

        write_rules(self.model, self.psl_learned_rule_file)
