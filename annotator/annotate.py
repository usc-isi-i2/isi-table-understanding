import numpy as np
from cell_classifier.cell_classifier import CellClassifier
from block_extractor.simple_block_extractor import BlockExtractor
from layout_detector.layout_detector import LayoutDetector
from annotator.abstract_annotator import AbstractAnnotator

# TODO: Change name of this file and class
class Annotator:  # TODO: Subclass of annotator?
    @staticmethod
    def get_annotation(sheet_index: int, sheet: np.array, cell_classifier: CellClassifier, block_extractor: BlockExtractor,
                       layout_detector: LayoutDetector, annotator: AbstractAnnotator):
        tags = cell_classifier.classify_cells(sheet)
        blocks = block_extractor.extract_blocks(sheet, tags)
        layout = layout_detector.detect_layout(sheet, tags, blocks)

        print("Blocks found:")

        for idx, block in enumerate(blocks):
            print("Block id: " + str(idx) + " " + str(block))

        print("\nLayout:")

        for idx, edges in enumerate(layout):
            print("FROM " + str(idx) + " TO " + str(edges))

        return annotator.get_annotation(sheet_index, sheet, tags, blocks, layout)
