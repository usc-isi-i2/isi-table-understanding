from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
import pickle
import numpy as np
from type.cell.semantic_cell_type import SemanticCellType
from type.cell.cell_type_pmf import CellTypePMF
from sklearn.metrics import f1_score
from imblearn.ensemble import BalancedRandomForestClassifier
from sklearn.model_selection import GridSearchCV
import itertools
from cell_classifier.mlp.model import MLP, MLPloader
from torch.utils.data import DataLoader
import torch

class MLPClassifierTrainer:

    def __init__(self, model_file):
        self.model_file = model_file
        print(self.model_file)

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
        print(X_eval.shape, y_eval.shape, y_eval[0])
        #print("train", np.bincount(y_train))
        #print("eval", np.bincount(y_eval))

        best_model = None
        best_loss = 100000
        for lr in [0.01, 0.001, 0.0001]:
            loader = DataLoader(dataset=MLPloader(X_train, y_train), batch_size=32,
                                     shuffle=True)
            model = MLP(X_train.shape[1], len(SemanticCellType.id2str)).to(torch.device("cuda:0"))
            loss_fn = torch.nn.CrossEntropyLoss()
            optimizer = torch.optim.SGD(model.parameters(), lr = 0.0001)
            train_loss = 0

            for epoch in range(100):
                for batch_idx, (data,label) in enumerate(loader):

                    data = data.to(torch.device("cuda:0")).float()

                    label = label.to(torch.device("cuda:0"))

                    optimizer.zero_grad()

                    out = model(data)

                    loss = loss_fn(out, label)

                    loss.backward()

                    train_loss += loss.item()
                    optimizer.step()

                if batch_idx % 50 == 0:
                    print('====> Epoch: {} Average loss: {:.4f}'.format(epoch, train_loss / len(loader.dataset)))

            if train_loss / len(loader.dataset) < best_loss:
                best_loss = train_loss / len(loader.dataset)
                best_model = model

        self.model = best_model
        self.save_model()

    def save_model(self):
        torch.save(self.model.state_dict(), self.model_file)
        #dump(self.model, self.model_file)
