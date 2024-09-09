from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
import pickle
import numpy as np
from type.cell.semantic_cell_type import SemanticCellType
from type.cell.cell_type_pmf import CellTypePMF
from sklearn.metrics import f1_score
import itertools

class C2VClassifierTrainer:

    def __init__(self, model_file):

        self.model_file = model_file
        print(self.model_file)

        self.n_estimators = [100, 300]
        self.max_depth = [5, 50, None]
        self.min_samples_split = [2, 10]
        self.min_samples_leaf = [1, 10]

    def prepare_data(self, sheets, tags):
        feats = [sheet.meta['embeddings'][i][j] for sheet in sheets
                    for i in range(sheet.values.shape[0])
                    for j in range(sheet.values.shape[1])]
        y = [tag[i][j].get_best_type().id() for tag in tags
                    for i in range(len(tag))
                    for j in range(len(tag[i]))]
        feats = np.array(feats)
        y = np.array(y)
        return feats, y

    def predict_wrapper(self, res, r, c):

        pred = np.empty((r, c), dtype=CellTypePMF)

        idx = 0

        for i in range(r):
            for j in range(c):
                t_id = res[idx]
                t_l = SemanticCellType.id2str[t_id]

                cell_class_dict = {
                    SemanticCellType.inverse_dict[t_l]: 1.0
                }
                pred[i][j] = CellTypePMF(cell_class_dict)

                idx += 1

        return pred

    def fit(self, sheets, tags, eval_sheets, eval_tags):
        X_train, y_train = self.prepare_data(sheets, tags)
        X_eval, y_eval = self.prepare_data(eval_sheets, eval_tags)
        print(X_eval.shape, y_eval.shape)

        best_score = 0
        best_model = None

        combs = [self.n_estimators, self.max_depth, self.min_samples_split,
                 self.min_samples_leaf]
        for para in list(itertools.product(*combs)):
            print(para)
            (n_es, dep, m_split, m_leaf) = para
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
