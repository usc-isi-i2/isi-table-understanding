
from cell_classifier.cell_classifier import CellClassifier
from block_extractor.block_extractor import BlockExtractor
from layout_detector.layout_detector import LayoutDetector
from reader.file_reader import get_file_reader


import sys, traceback
import time
import logging

class EndToEnd:
    """
    Class for creating end-to-end table understanding pipelines
    These pipelines will apply cell classification, block extraction, and layout detection
    """
    def __init__(self, cell_classifier: CellClassifier, block_extractor: BlockExtractor, layout_detector: LayoutDetector):
        """

        :param cell_classifier: Fully-qualified class name of a CellClassifier
        :param block_extractor: Fully-qualified class name of a BlockExtractor
        :param layout_detector: Fully-qualified class name of a LayoutDetector
        """
        self.cell_classifier = cell_classifier
        self.block_extractor = block_extractor
        self.layout_detector = layout_detector

    def print_sheet(self, sheet):
        if sheet.meta is None:
            logging.warning("Sheet meta is undefined. ")
        else:
            logging.debug("Processing sheet: {}".format(sheet.meta['name']))

    def get_layout(self, input_file):
        start_time = time.time()

        reader = get_file_reader(input_file)

        sheetList, tagList, blockList, layoutList = [], [], [], []

        for sheet in reader.get_sheets():
            tags, blocks, layout = [[]], [], None
            try:
                self.print_sheet(sheet)
                tags = self.cell_classifier.classify_cells(sheet)
                blocks = self.block_extractor.extract_blocks(sheet, tags)
                layout = self.layout_detector.detect_layout(sheet, tags, blocks)
            except Exception as e:
                logging.error(str(e))
                traceback.print_exc(file=sys.stdout)

            sheetList.append(sheet)
            tagList.append(tags)
            blockList.append(blocks)
            layoutList.append(layout)

        end_time = time.time()

        logging.debug("Time taken to process sheets: {}".format(end_time - start_time))

        return sheetList, tagList, blockList, layoutList
