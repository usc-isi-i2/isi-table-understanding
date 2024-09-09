import numpy as np
from cell_classifier.crf_cell_classifier import CRFCellClassifier
from cell_classifier_crf.featurize_labels import inverse_dict, label_dict


class CRFCellClassifierBenchmark:
    def __init__(self, sheet: np.array, crf_classifier: CRFCellClassifier, gold: np.array):
        self.sheet = sheet
        self.crf_classifier = crf_classifier
        self.gold = gold

    def get_confusion_matrix(self):
        tags = self.crf_classifier.classify_cells(self.sheet)
        num_labels = len(inverse_dict)

        confusion_matrix = np.zeros((num_labels, num_labels), dtype=int)

        assert tags.shape == self.gold.shape, "Predicted output shape and gold output shape do not match"

        tags = tags.reshape(-1)
        gold = self.gold.reshape(-1)

        for x, y in zip(tags, gold):
            label_pred = x.get_best_type()
            label_gold = y.get_best_type()

            confusion_matrix[label_dict[label_pred]][label_dict[label_gold]] += 1

        return confusion_matrix
