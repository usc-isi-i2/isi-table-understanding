from configurator.configurator import Configurator
import unittest
import yaml

from cell_classifier.crf_cell_classifier import CRFCellClassifier
from block_extractor.block_extractor_decision_tree import BlockExtractorDecisionTree
from layout_detector.crf.crf_layout_detector import CRFLayoutDetector

class TestConfigurator(unittest.TestCase):
    def testConfigurator(self):
        config_file = "../../cfg/default.yaml"
        config = yaml.load(open(config_file))

        configurator = Configurator(config)

        assert isinstance(configurator.get_component("cell_classifier"), CRFCellClassifier)

        block_extractor = configurator.get_component("block_extractor")
        assert block_extractor.threshold == 0.3
        assert isinstance(block_extractor, BlockExtractorDecisionTree)

        assert isinstance(configurator.get_component("layout_detector"), CRFLayoutDetector)
