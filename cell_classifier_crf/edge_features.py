from cell_classifier_crf.edge_map import get_edge_map
from util.string_utils import string2int, data_to_string
import numpy as np


def get_row_col(num, r, c) -> (int, int):
    row = int(num / c)
    col = num % c

    return row, col


# Edge feature functions
def is_increment(x1, x2):
    x1 = string2int(x1)
    x2 = string2int(x2)

    if x1 and x2 and x2 == x1 + 1:
        return 1
    return 0


def is_decrement(x1, x2):
    x1 = string2int(x1)
    x2 = string2int(x2)

    if x1 and x2 and x2 == x1 - 1:
        return 1
    return 0


def is_equal_int(x1, x2):
    # integer and equal
    x1 = string2int(x1)
    x2 = string2int(x2)

    if x1 and x2 and x2 == x1:
        return 1
    return 0


# TODO: Or functions should be automatically built
def is_increment_or_decrement_or_equal(x1, x2):
    return is_increment(x1, x2) | is_decrement(x1, x2) | is_equal_int(x1, x2)


# https://stackoverflow.com/questions/2460177/edit-distance-in-python
# Modified to consider any digits as equal
def edit_distance_replace_number_with_hash(s1, s2):
    s1 = data_to_string(s1)
    s2 = data_to_string(s2)

    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            # Any two digits are considered equal
            if (c1.isdigit() and c2.isdigit()) or c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def edit_distance(s1, s2):
    s1 = data_to_string(s1)
    s2 = data_to_string(s2)

    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            # Two digits are NOT considered equal
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def get_edge_map_and_features(x, x_fz, dist=1):
    row, col, num_node_features = x_fz.shape

    edge_map = get_edge_map(row, col, dist=1)

    # Could this be vectorized?
    edge_functions = 6 + 3  # TODO: do not hardcode?
    num_edge_features = num_node_features * 3 + edge_functions
    edge_features = np.zeros((len(edge_map), num_edge_features))

    for i, edge in enumerate(edge_map):
        l, r = edge[0], edge[1]
        r1, c1 = get_row_col(l, row, col)
        r2, c2 = get_row_col(r, row, col)

        edge_features[i][:num_node_features] = x_fz[r1][c1]
        edge_features[i][num_node_features:num_node_features * 2] = x_fz[r2][c2]
        edge_features[i][num_node_features * 2:num_node_features * 3] = x_fz[r1][c1] & x_fz[r2][c2]

        dist = edit_distance_replace_number_with_hash(x[r1][c1], x[r2][c2])
        if dist == 0:
            edge_features[i][-4] = 1
        if dist <= 1:
            edge_features[i][-5] = 1
        if dist <= 4:
            edge_features[i][-6] = 1

        dist = edit_distance(x[r1][c1], x[r2][c2])
        if dist == 0:
            edge_features[i][-7] = 1
        if dist <= 1:
            edge_features[i][-8] = 1
        if dist <= 4:
            edge_features[i][-9] = 1

        edge_features[i][-3] = is_increment_or_decrement_or_equal(x[r1][c1], x[r2][c2])

        if l + 1 == r:
            edge_features[i][-2] = 1
        else:
            edge_features[i][-1] = 1

    # return edge_map, np.zeros((len(edge_map), num_edge_features))
    return edge_map, edge_features
