import numpy as np

# Must match whole words
# Eg. Yearly is not a time label hint. It can be a description of some measure
# TODO: Should give weights to these matches

time_label_hints = 'year yyyy quarter month day date time'.split()
measure_label_hints = 'total count average quantity value price amount'.split() #'index' is ambiguous
description_hints = 'of for the and'.split()

"""
Helper function
Find all the cells which have keywords that hint whether the cell is a time label or meta data
"""


def match_hints(hints, sheet):
    features = np.zeros(sheet.shape, dtype=int)
    r, c = sheet.shape

    for i in range(r):
        for j in range(c):
            for hint in hints:
                # TODO: Match whole words #regex match re.IGNORECASE
                # TODO: Handle other datatypes (datetime, number, etc)
                val = sheet[i][j]
                if isinstance(val, str):
                    if hint in val.lower():
                        features[i][j] = 1

    return features


# QUESTION: should the cell with the hint be marked as 1 or 0 in th output
"""
Helper function
Create a feature vector with all cells in the given axis receiving known hints
"""


def propagate_hints(features, axis):
    r, c = features.shape
    y = np.array(np.sum(features, axis=axis) > 0, dtype=int)

    if axis == 1:
        # TO remove the original hints: do an xor with features
        return np.tile(y, (c, 1)).T
    else:  # axis=0
        return np.tile(y, (r, 1))


def get_long_range_features(sheet, hints):
    f = match_hints(hints, sheet)
    fv = (propagate_hints(f, 1) | propagate_hints(f, 0)) ^ f

    return fv


def merge_all_long_range_features(sheet):
    fv1 = get_long_range_features(sheet, time_label_hints)
    fv2 = get_long_range_features(sheet, measure_label_hints)

    fv = np.stack([fv1, fv2], axis=-1)

    return fv


