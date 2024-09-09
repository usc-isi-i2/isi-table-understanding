from cell_classifier.cell_classifier import CellClassifier
from joblib import dump, load
import numpy as np
from type.cell.semantic_cell_type import SemanticCellType
from type.cell.cell_type_pmf import CellTypePMF
from reader.sheet import Sheet
from typing import List
import sys
import numpy as np
from cell_classifier.mlp.model import MLP, MLPloader
import torch

class MLPCellClassifierV2(CellClassifier):
    def __init__(self, model_file):
        print(model_file)
        self.model = MLP(552, len(SemanticCellType.id2str))
        self.model.load_state_dict(torch.load(model_file))
        self.model.eval()

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

    def classify_cells(self, sheet: Sheet) -> 'np.ndarray[CellTypePMF]':
        embs = sheet.meta['embeddings']

        r, c = sheet.values.shape

        feat = [embs[i][j] for i in range(r) for j in range(c)]

        feat = torch.from_numpy(np.array(feat)).float()

        #m = torch.nn.Softmax(dim=1)

        #torch.max(outputs, 1)

        result = torch.argmax(self.model(feat), dim=1).cpu().detach().numpy()

        #print(result.shape, r, c, result[0])

        tags = self.predict_wrapper(result, r, c)

        return tags

    def classify_cells_all_tables(self, sheets):
        tags = []

        for sheet in sheets:

            tags.append(self.classify_cells(sheet))

        return tags

