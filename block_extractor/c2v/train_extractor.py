from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
import pickle
import numpy as np
from type.block.simple_block import SimpleBlock
from type.block.block_type_pmf import BlockTypePMF
from type.block.function_block_type import FunctionBlockType
import itertools
from sklearn.metrics import f1_score

class C2VExtractorTrainer:

    def __init__(self, model_file):
        self.model_file = model_file
        print(self.model_file)
        self.n_estimators = [100, 300]
        self.max_depth = [5, 50, None]
        self.min_samples_split = [2, 10]
        self.min_samples_leaf = [1, 10]

    def prepare_data(self, sheets, tags):
        feats, y = [], []
        for sid, sheet in enumerate(sheets):
            for block in tags[sid]:
                lx, ly = block.top_row, block.left_col
                rx, ry = block.bottom_row, block.right_col
                lab = block.block_type.get_best_type()

                for i in range(lx, rx + 1):
                    for j in range(ly, ry + 1):
                        feats.append(sheet.meta["embeddings"][i][j])
                        y.append(lab.id())

        feats = np.array(feats)
        y = np.array(y)
        return feats, y

    def fit(self, sheets, tags, eval_sheets, eval_tags):
        X_train, y_train = self.prepare_data(sheets, tags)
        X_eval, y_eval = self.prepare_data(eval_sheets, eval_tags)

        best_score = 0
        best_model = None
        combs = [self.n_estimators, self.max_depth, self.min_samples_split,
                 self.min_samples_leaf]
        for para in list(itertools.product(*combs)):
            (n_es, dep, m_split, m_leaf) = para
            print(para)
            model = RandomForestClassifier(max_depth=dep, n_estimators=n_es,
                                           random_state=0, n_jobs=50,
                                           class_weight="balanced_subsample",
                                           bootstrap=True,
                                           min_samples_split=m_split,
                                           min_samples_leaf=m_leaf
                                           )
            model.fit(X_train, y_train)
            preds = model.predict(X_eval)
            score = f1_score(y_eval, preds, average="macro")

            if score > best_score:
                best_score = score
                best_model = model

        self.model = best_model
        self.save_model()

    def save_model(self):
        dump(self.model, self.model_file)
