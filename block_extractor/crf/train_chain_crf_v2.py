from type.cell.function_cell_type import FunctionCellType
from pystruct.models import ChainCRF
from pystruct.learners import OneSlackSSVM
import pickle
from joblib import dump, load
from block_extractor.crf.featurize import *
import numpy as np
from sklearn.metrics import f1_score

class ChainCRFTrainer:

    def __init__(self, model_file):
        self.model_file = model_file

        self.max_iter = 1000
        self.C_range = [0.1, 0.3, 0.5, 0.7, 1.0]
        self.tol = 0.01
        self.eval_against_test = False

    def prepare_data(self, sheets, tags):
        feats = []
        y = []
        for sid, sheet in enumerate(sheets):
            labs = get_row_labels(sheet, tags[sid])
            feat = get_row_feats(sheet)
            temp_feats, temp_labs = [], []

            for i in range(len(labs)):
                if FunctionCellType.id2str[labs[i]] == "empty":
                    continue
                temp_feats.append(feat[i])
                temp_labs.append(labs[i])
            if len(temp_feats) == 0:
                continue
            feats.append(np.array(temp_feats))
            y.append(np.array(temp_labs))
        return feats, y

    def fit(self, sheets, tags, eval_sheets, eval_tags):
        print(len(sheets), len(eval_sheets))
        X_train, y_train = self.prepare_data(sheets, tags)
        X_eval, y_eval = self.prepare_data(eval_sheets, eval_tags)

        best_model = None
        best_score = -1
        best_C = 0

        for C in self.C_range:
            model = ChainCRF(inference_method="ad3")
            ssvm = OneSlackSSVM(model, inference_cache=50, C=C, tol=self.tol, max_iter=self.max_iter, n_jobs=20, verbose=False)
            ssvm.fit(X_train, y_train)

            predictions = ssvm.predict(X_eval)
            eval_list, pred_list = [], []
            for i, sheet in enumerate(eval_sheets):
                pred_list += predictions[i].tolist()
                eval_list += y_eval[i].tolist()

            score = f1_score(eval_list, pred_list, average="macro")

            if score > best_score:
                best_score = score
                best_model = ssvm
                best_model = ssvm
                best_C = C

        print("best_C", best_C)
        self.model = best_model
        self.save_model()

    def save_model(self):
        dump(self.model, self.model_file)
