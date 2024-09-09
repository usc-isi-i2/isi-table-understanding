from cell_classifier.cell_classifier import CellClassifier
import pickle
from cell_classifier_crf.featurize_input import featurize_input
import numpy as np
from cell_classifier_crf.edge_features import get_edge_map_and_features
from type.cell.basic_cell_type import BasicCellType
from config import config, get_full_path
from type.cell.cell_type_pmf import CellTypePMF
from reader.sheet import Sheet
from typing import List

from cell_classifier_crf.featurize_labels import inverse_dict

class CRFCellClassifier(CellClassifier):
    def __init__(self):
        crf_model_file = get_full_path(config['crf']['cell_classifier_model_file'])
        with open(crf_model_file, 'rb') as infile:
            self.model = pickle.load(infile, encoding='latin1')  # latin1 encoding since we are reading a python2 pickle file

    def __predict_wrapper(self, prediction, r, c):
        pred = np.empty((r, c), dtype=CellTypePMF)
        for i in range(r):
            for j in range(c):
                cell_class_dict = {
                    inverse_dict[prediction[i*c + j]]: 1.0
                }
                pred[i][j] = CellTypePMF(cell_class_dict)

        return pred

    def __get_features(self, sheet: Sheet):
        x = sheet.values
        x_fz = featurize_input(sheet.values)
        num_features = x_fz.shape[2]
        x_graph = (
                    (np.reshape(x_fz, (x_fz.shape[0] * x_fz.shape[1], num_features)),) +
                    get_edge_map_and_features(x, x_fz, dist=1)
        )
        return np.array(x_graph)

    def classify_cells(self, sheet: Sheet) -> 'np.ndarray[CellTypePMF]':
        x_graph = self.__get_features(sheet)
        predictions = self.model.predict([x_graph])[0]  # TODO (minor): Direct access by index should be avoided
        tags = self.__predict_wrapper(predictions, sheet.values.shape[0], sheet.values.shape[1])

        return tags
