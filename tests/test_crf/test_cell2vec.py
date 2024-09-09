import unittest
from cell_classifier_crf.cell2vec import cell2vec
import numpy as np


class TestCell2Vec(unittest.TestCase):
    def test_cell2vec(self):
        value = '1/1/18'
        assert np.array_equal(cell2vec(value).vec(), [1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
