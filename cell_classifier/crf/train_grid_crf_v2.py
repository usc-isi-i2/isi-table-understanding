from cell_classifier.crf.featurize_v2 import *
from pystruct.models import GridCRF
from pystruct.learners import OneSlackSSVM
import pickle
from joblib import dump, load
import numpy as np
from type.cell.cell_type_pmf import CellTypePMF
from type.cell.semantic_cell_type import SemanticCellType
from sklearn.metrics import f1_score

class GridCRFTrainer:

    def __init__(self, model_file):
        self.model_file = model_file
        self.max_iter = 500
        self.C_range = [0.01, 0.05, 0.1]
        self.tol = 0.01
        self.eval_against_test = False

    def prepare_data(self, sheets, tags):
        feats = []
        y = []
        for sid, sheet in enumerate(sheets):
            r, c = sheet.values.shape
            tag = tags[sid]
            temp = [[sheet.meta['farr'][i][j] for j in range(c)] for i in range(r)]
            temp_y = [[tag[i][j].get_best_type().id() for j in range(c)] for i in range(r)]
            if len(temp[0]) <= 1:
                continue

            feats.append(np.array(temp))
            y.append(np.array(temp_y))
            print("feat", len(temp), "y", len(temp_y), "col", len(temp[0]))

        return feats, y

    def __predict_wrapper(self, prediction, r, c):
        pred = np.empty((r, c), dtype=CellTypePMF)
        for i in range(r):
            for j in range(c):
                cell_class_dict = {
                    SemanticCellType.id2obj[prediction[i][j]]: 1.0
                }
                pred[i][j] = CellTypePMF(cell_class_dict)
        return pred

    def fit(self, sheets, tags, eval_sheets, eval_tags):
        X_train, y_train = self.prepare_data(sheets, tags)
        X_eval, y_eval = self.prepare_data(eval_sheets, eval_tags)
        best_model = None
        best_score = 0
        for C in self.C_range:
            model = GridCRF(inference_method="ad3")
            ssvm = OneSlackSSVM(model, inference_cache=50, C=C, tol=self.tol, max_iter=self.max_iter, n_jobs=40, verbose=True)
            print(len(X_train), len(y_train))
            ssvm.fit(X_train, y_train)

            predictions = ssvm.predict(X_eval)

            eval_list, pred_list = [], []
            for i, sheet in enumerate(eval_sheets):
                #print(predictions[i].shape)
                for j in range(len(predictions[i])):
                    pred_list += predictions[i][j].tolist()
                    eval_list += y_eval[i][j].tolist()
            #celltypes = []
            #predictions = ssvm.predict(X_eval)
            #print(len(eval_list), len(pred_list))

            score = f1_score(eval_list, pred_list, average="macro")

            if score > best_score:
                best_score = score
                best_model = ssvm

        print("finish fitting")
        self.model = best_model
        self.save_model()

    def save_model(self):
        dump(self.model, self.model_file)
