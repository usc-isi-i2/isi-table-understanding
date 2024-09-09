import unittest
from data_loader.load_training_data import LoadTrainingData


# TO RUN: python -m unittest tests.data_loader_test.load_training_data_test
class LoadTrainingDataTest(unittest.TestCase):
    def testLoadTrainingData(self):
        data_loader = LoadTrainingData(data_path="data/layout_files")

        b, l = data_loader.load_annotation_files()

        print(len(b), len(l))
        print("{} annotation files loaded. ".format(len(b)))
