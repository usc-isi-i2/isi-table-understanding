import unittest
from data_loader.load_synthetic_data import LoadSyntheticData


# TO RUN: python -m unittest tests.data_loader_test.load_synthetic_data_test
class LoadSyntheticDataTest(unittest.TestCase):
    def testLoadSyntheticData(self):
        data_loader = LoadSyntheticData()

        s, c, b, l = data_loader.load_files()

        print(len(s), len(c), len(b), len(l))
        print("{} files loaded. ".format(len(b)))

        print(s[0])
        print(c[0])

        assert s[0].shape == c[0].shape

