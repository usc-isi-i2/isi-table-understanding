from layout_detector.random_forest.featurize import *
from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
import pickle
import numpy as np
from sklearn.metrics import f1_score

class RFClassifierTrainer:

    def __init__(self, model_file):

        self.model_file = model_file

        self.n_estimators = [100, 300]
        self.max_depth = [5, 50, None]
        self.min_samples_split = [2, 10]
        self.min_samples_leaf = [1, 10]


    def prepare_data(self, sheets, graphs):
        feats, y = [], []
        for i, graph in enumerate(graphs):
            pairs, labels = get_block_labels(graph)
            y += labels
            blks = graph.nodes
            for (pi, pj) in pairs:
                feats.append(block_relation_feats(blks[pi], blks[pj]))
        feats = np.array(feats)
        y = np.array(y)
        return feats, y

    def fit(self, sheets, graphs, eval_sheets, eval_graphs):
        X_train, y_train = self.prepare_data(sheets, graphs)
        X_eval, y_eval = self.prepare_data(eval_sheets, eval_graphs)
        best_model = None
        best_score = 0
        import itertools
        combs = [self.n_estimators, self.max_depth, self.min_samples_split,
                 self.min_samples_leaf]
        for para in list(itertools.product(*combs)):
            #print(para)
            (n_es, dep, m_split, m_leaf) = para
            model = RandomForestClassifier(max_depth=dep, n_estimators=n_es,
                                           random_state=0, n_jobs=50,
                                           class_weight="balanced_subsample",
                                           bootstrap=True,
                                           min_samples_split=m_split,
                                           min_samples_leaf=m_leaf
                                           )

            model.fit(X_train, y_train)

            pred = model.predict(X_eval)
            metric = f1_score(y_eval, pred, average="macro")

            if metric > best_score:
                best_score = metric
                best_model = model

        self.model = best_model
        self.save_model()

    def save_model(self):
        dump(self.model, self.model_file)
