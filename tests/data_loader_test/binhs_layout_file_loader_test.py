import unittest
from data_loader.binhs_layout_file_loader import BinhsLayoutFileLoader

# python -m unittest tests.data_loader_test.binhs_layout_file_loader_test

class TestBinhsLayoutFileLoader(unittest.TestCase):
    def testLayoutFileLoader(self):
        lfl = BinhsLayoutFileLoader("data/sample.yaml")

        tags, blocks, layout = lfl.get_cell_tags_blocks_and_layout()

        print(tags)
        for block in blocks:
            print(block)
        print(layout.inEdges)
        print(layout.outEdges)
