from cell_classifier.cell_classifier import CellClassifier
import pickle
from joblib import dump, load
import numpy as np
from type.cell.semantic_cell_type import SemanticCellType
from type.cell.cell_type_pmf import CellTypePMF
from reader.sheet import Sheet
from typing import List

class GridCRFCellClassifierV2(CellClassifier):
    def __init__(self, crf_model_file):
        print(crf_model_file)
        self.model = load(crf_model_file)

    def __predict_wrapper(self, prediction, r, c):
        pred = np.empty((r, c), dtype=CellTypePMF)
        for i in range(r):
            for j in range(c):
                cell_class_dict = {
                    SemanticCellType.id2obj[prediction[i][j]]: 1.0
                }
                pred[i][j] = CellTypePMF(cell_class_dict)
        return pred

    def get_features(self, sheets):
        feats = []
        for sid, sheet in enumerate(sheets):
            r, c = sheet.values.shape
            temp = [[sheet.meta['farr'][i][j] for j in range(c)] for i in range(r)]

            feats.append(np.array(temp))
        return feats

    def classify_cells(self, sheet: Sheet) -> 'np.ndarray[CellTypePMF]':
        x_test = self.get_features([sheet])
        predictions = self.model.predict(x_test)[0]
        r, c = sheet.values.shape
        tags = self.__predict_wrapper(predictions, r, c)
        return tags

    def classify_cells_all_tables(self, sheets):
        x_test = self.get_features(sheets)
        predictions = self.model.predict(x_test)
        tags = [self.__predict_wrapper(predictions[i],
                    sheet.values.shape[0], sheet.values.shape[1])
                for i, sheet in enumerate(sheets)]
        return tags
