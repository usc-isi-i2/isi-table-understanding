
from cell_classifier.cell_classifier import CellClassifier
from block_extractor.block_extractor import BlockExtractor
from layout_detector.layout_detector import LayoutDetector
from reader.file_reader import get_file_reader
from preprocess import PreprocessCE

import sys, traceback
import time


class EndToEnd:
    def __init__(self, cell_classifier: CellClassifier, block_extractor: BlockExtractor, layout_detector: LayoutDetector, args):
        self.cell_classifier = cell_classifier
        self.block_extractor = block_extractor
        self.layout_detector = layout_detector
        if "ce_source" in args:
            self.preprocessor = PreprocessCE(args)
        else:
            self.preprocessor = None

    def print_sheet(self, sheet):
        if sheet.meta is None:
            print("Sheet meta is undefined. ")
        else:
            print("Processing sheet: {}".format(sheet.meta['name']))

    def get_layout(self, input_file):
        start_time = time.time()

        sheetList, tagList, blockList, layoutList = [], [], [], []

        if self.preprocessor is None:
            reader = get_file_reader(input_file)
            sheets = [sheet for sheet in reader.get_sheets()]
        else:
            sheets = self.preprocessor.process_tables(input_file)

        for sheet in sheets:
            tags, blocks, layout = [[]], [], None
            try:
                self.print_sheet(sheet)
                tags = self.cell_classifier.classify_cells(sheet)
                blocks = self.block_extractor.extract_blocks(sheet, tags)
                layout = self.layout_detector.detect_layout(sheet, tags, blocks)
            except Exception as e:
                print(str(e))
                traceback.print_exc(file=sys.stdout)

            sheetList.append(sheet)
            tagList.append(tags)
            blockList.append(blocks)
            layoutList.append(layout)

        end_time = time.time()

        print("Time taken to process sheets : ", (end_time - start_time), "s")

        return sheetList, tagList, blockList, layoutList
