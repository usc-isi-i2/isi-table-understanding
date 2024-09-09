import unittest
from data_loader.layout_file_loader import LayoutFileLoader


class TestLayoutFileLoader(unittest.TestCase):
    def testLayoutFileLoader(self):
        lfl = LayoutFileLoader("/Users/work/Projects/table-understanding/data/layout_files/wits_trade_summary/ann.json")

        blocks, layout = lfl.get_blocks_and_layout()[0]

        for block in blocks:
            print(block)

        assert layout.outEdges == [[('header', 2)], [('meta', 3)], [('meta', 3)], []]
        assert layout.inEdges == [[], [], [('header', 0)], [('meta', 1), ('meta', 2)]]

    def testMultiLayoutFileLoader(self):
        lfl = LayoutFileLoader("/Users/work/Projects/table-understanding/data/layout_files/global_database_for_pulses_on_dry_matter_basis/ann.json")

        blocks, layout = lfl.get_blocks_and_layout()[0]

        for block in blocks:
            print(block)

        assert layout.outEdges == [[('header', 1)], []]
        assert layout.inEdges == [[], [('header', 0)]]
