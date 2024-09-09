from pystruct.models import EdgeFeatureGraphCRF
from pystruct.learners import OneSlackSSVM
import pickle
from joblib import dump, load
from layout_detector.crf.featurizer_v2 import *
import numpy as np
from sklearn.metrics import f1_score

class GraphCRFTrainer:

    def __init__(self, model_file):
        self.model_file = model_file
        self.max_iter = 100
        self.C_range = [0.01, 0.05, 0.1]
        self.tol = 0.01
        self.eval_against_test = False

    def prepare_data(self, sheets, graphs):
        feats = []
        y = []
        for graph in graphs:
            temp_feat = get_input_features_for_table(graph.nodes)
            temp_y = get_label_map(graph)

            feats.append((temp_feat[0], temp_feat[1], temp_feat[2]))
            y.append(temp_y)
        return feats, y

    def fit(self, sheets, graphs, eval_sheets, eval_graphs):
        X_train, y_train = self.prepare_data(sheets, graphs)
        X_eval, y_eval = self.prepare_data(eval_sheets, eval_graphs)
        print(len(X_train), len(y_train), len(X_eval), len(y_eval))

        best_model = None
        best_score = 0
        for C in self.C_range:
            model = EdgeFeatureGraphCRF(inference_method="ad3")
            ssvm = OneSlackSSVM(model, inference_cache=50, C=C, tol=self.tol, max_iter=self.max_iter, n_jobs=60, verbose=False)
            print("start fitting")
            ssvm.fit(X_train, y_train)
            print("end fitting")

            pred = ssvm.predict(X_eval)
            temp_eval = [_ for l in y_eval for _ in l]
            pred = [_ for l in pred for _ in l]
            print(len(temp_eval), len(pred))
            metric = f1_score(temp_eval, pred, average="macro")

            if metric > best_score:
                best_score = metric
                best_model = ssvm

        self.model = best_model
        self.save_model()

    def save_model(self):
        dump(self.model, self.model_file)
