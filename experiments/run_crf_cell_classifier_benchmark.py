from benchmarks.crf_cell_classifier_benchmark import CRFCellClassifierBenchmark
from data_loader.load_synthetic_data import LoadSyntheticData
from cell_classifier.crf_cell_classifier import CRFCellClassifier
import numpy as np
from cell_classifier_crf.featurize_labels import inverse_dict


def run_crf_cell_classifier_benchmark():
    lst = LoadSyntheticData()
    sheets, cell_tags, blocks, layout = lst.load_files()
    crf_classifier = CRFCellClassifier()

    num_labels = len(inverse_dict)
    confusion_matrix = np.zeros((num_labels, num_labels), dtype=int)

    for sheet, cell_tag in zip(sheets, cell_tags):
        cccb = CRFCellClassifierBenchmark(sheet, crf_classifier, cell_tag)
        confusion_matrix += cccb.get_confusion_matrix()
        print("Tagged.")

    print(confusion_matrix)


if __name__ == "__main__":
    run_crf_cell_classifier_benchmark()