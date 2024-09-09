import numpy as np

def edit_distance_score(table):
    epsilon = 1e-6
    row, col = table.shape
    assert row >= 3
    edit_distance_matrix = np.zeros((row - 1, col))

    for i in range(row - 1):
        for j in range(col):
            edit_distance_matrix[i][j] = edit_distance(table[i][j], table[i + 1][j])

    # Normalize mean and sd for each column to avoid variations in 1 column affecting the answer
    col_mean = np.mean(edit_distance_matrix, axis=0)
    col_std = np.std(edit_distance_matrix, axis=0) * (row - 1) / (row - 2)  # Applying bessel's correction to sd

    edit_distance_matrix -= col_mean
    edit_distance_matrix /= (col_std + epsilon)

    row_sum = np.sum(edit_distance_matrix, axis=1)
    prev_sum = 0
    for i, e in reversed(list(enumerate(row_sum))):
        row_sum[i] += prev_sum
        prev_sum = row_sum[i]

    print(row_sum)
    return row_sum


# https://stackoverflow.com/questions/2460177/edit-distance-in-python
# Modified to consider any digits as equal
def edit_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            #Two digits are considered equal
            if (c1.isdigit() and c2.isdigit()) or c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]