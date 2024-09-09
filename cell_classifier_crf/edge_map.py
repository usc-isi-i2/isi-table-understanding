import numpy as np


def get_edge_map(r, c, dist=1):
    left = []
    right = []
    for i in range(r):
        for j in range(c):
            num = i * c + j

            for k in range(dist):
                if i + k + 1 < r:
                    left.append(num)
                    right.append((i + k + 1) * c + j)

            for k in range(dist):
                if j + k + 1 < c:
                    left.append(num)
                    right.append(i * c + j + k + 1)

    return np.column_stack([left, right])
