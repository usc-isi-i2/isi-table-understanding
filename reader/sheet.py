import numpy as np


"""    
    Sheet:
        -values: np.array of cell values
        -meta: dict/feature vector of cell format for each cell
"""


class Sheet:
    def __init__(self, values: np.array, meta: np.array):
        self.values = values
        self.meta = meta
