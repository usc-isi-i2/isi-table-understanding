from cell_classifier.cell_classifier import CellClassifier
from block_extractor.block_extractor import BlockExtractor
from layout_detector.layout_detector import LayoutDetector
import numpy as np
import abc


class TableUnderstandingPipeline(abc.ABC):
    def __init__(self, cell_classifier: CellClassifier, block_extractor: BlockExtractor, layout_detector: LayoutDetector):
        self.cell_classifier = cell_classifier
        self.block_extractor = block_extractor
        self.layout_detector = layout_detector

    @abc.abstractmethod
    def predict(self, sheet: np.array):
        pass

    @abc.abstractmethod
    def evaluate(self, cell_tags, blocks, layout):
        pass
