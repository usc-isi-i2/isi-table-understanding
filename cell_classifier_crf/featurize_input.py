from cell_classifier_crf.cell2vec import cell2vec
import numpy as np
from cell_classifier_crf.hints import merge_all_long_range_features


def featurize_input(sheet):
    num_features = len(cell2vec('sample').vec())

    r, c = sheet.shape
    x = np.zeros((r, c, num_features), dtype=int)
    # Unary potentials
    for j in range(r):
        for k in range(c):
            x[j][k] = cell2vec(sheet[j][k]).vec()

    long_range_features = merge_all_long_range_features(sheet)

    x = np.concatenate([x, long_range_features], axis=-1)
    return x
