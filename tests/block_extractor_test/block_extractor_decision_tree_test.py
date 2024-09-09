import unittest
import numpy as np
from type.cell.cell_type_pmf import CellTypePMF
from block_extractor.block_extractor_decision_tree import BlockExtractorDecisionTree
from reader.file_reader import get_file_reader


class TestDtreeExtractor(unittest.TestCase):
    def testDtreeExtractor(self):
        # Initialize block extractor input
        f_reader = get_file_reader("/Users/work/Downloads/tags.xlsx")

        sheet = f_reader.get_sheet_by_index(0)
        print(sheet.values.shape)

        tags = np.empty(sheet.values.shape, dtype=CellTypePMF)
        row, col = sheet.values.shape
        for i in range(row):
            for j in range(col):
                tags[i][j] = CellTypePMF({sheet.values[i][j]: 1})

        block_extractor = BlockExtractorDecisionTree(0.40)
        # TODO: Try .20 decision threshold
        blocks = block_extractor.extract_blocks(sheet, tags)

        for block in blocks:
            print(block)

        #TODO: Write a proper test
        ## Expected blocks: for threshold: 0.40
        # [(0,0) to (22,2)]
        # [(6,3) to (22,9)]
        # [(0,3) to (2,9)]
        # [(3,3) to (5,9)]

        # TODO: Write a test to check if splits and information gain is accurate.