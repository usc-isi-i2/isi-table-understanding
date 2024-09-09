import unittest
from annotator.yaml_annotator import YAMLAnnotator
from type.block.simple_block import SimpleBlock
from reader.csv_reader import CsvReader
from type.layout.layout_graph import LayoutGraph

class TestYAMLAnnotator(unittest.TestCase):
    def testIfCorrectAnnotationIsGenerated(self):
        yml = YAMLAnnotator()
        annotation = yml.get_annotation(None, None, None, None, None)
        yml.write_yaml(annotation, "test.yaml")


    def testFaocommodityAnnotation(self):
        csv_reader = CsvReader('../../data/FAOSTAT_commodity.csv')
        sheet = csv_reader.get_sheet_by_index(0)

        yml = YAMLAnnotator()

        blocks = []
        blocks.append(SimpleBlock("META", 0, 14, 0, 0))
        blocks.append(SimpleBlock("META", 1, 1, 1, 232))  # domain
        blocks.append(SimpleBlock("META", 3, 3, 1, 232))  # area
        blocks.append(SimpleBlock("DATE", 5, 5, 1, 232))  # year
        blocks.append(SimpleBlock("META", 7, 7, 1, 232))  # item
        blocks.append(SimpleBlock("_DATA_", 11, 11, 1, 232))  # value

        layout = LayoutGraph(blocks)

        layout.add_edge("header", 0, 1)
        layout.add_edge("header", 0, 2)
        layout.add_edge("header", 0, 3)
        layout.add_edge("header", 0, 4)
        layout.add_edge("header", 0, 5)
        layout.add_edge("meta", 1, 5)
        layout.add_edge("meta", 2, 5)
        layout.add_edge("meta", 3, 5)
        layout.add_edge("meta", 4, 5)

        annotation = yml.get_annotation(0, sheet, None, blocks, layout)

        yml.write_yaml(annotation, "../../data/FAOSTAT_commodity.yaml")
