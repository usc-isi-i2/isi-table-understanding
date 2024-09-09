import numpy as np
import yaml
import traceback
import sys

from configurator.configurator import Configurator
from reader.sheet import Sheet
from drepr.variable import Variable, Location, Slice, IndexSlice, RangeSlice
from type.block.simple_block import SimpleBlock


class ResourceAdapter:
    def __init__(self, data, resource_id, config_file="../cfg/resource_adapter_config.yaml"):
        self.data = data
        self.resource_id = resource_id

        # TODO: Avoid re-initializing every time
        # Initialize classifiers
        config = yaml.load(open(config_file))
        print("Using configuration: {}".format(config))
        configurator = Configurator(config)

        self.cell_classifier = configurator.get_component("cell_classifier")
        self.block_extractor = configurator.get_component("block_extractor")
        self.layout_detector = configurator.get_component("layout_detector")

    def get_variables(self):
        # Convert data to expected format
        data = np.array(self.data, ndmin=2)
        assert not isinstance(data[0][0], list), "Input data is not in correct format"
        assert len(data.shape) == 2, "Input data does not have correct number of dimensions"
        sheet = Sheet(data, None)

        tags, blocks, layout = None, None, None
        try:
            print("Processing sheet: {}".format(sheet.meta['name']))
            tags = self.cell_classifier.classify_cells(sheet)
            blocks = self.block_extractor.extract_blocks(sheet, tags)
            # layout = self.layout_detector.detect_layout(sheet, tags, blocks) # Use for alignments
        except Exception as e:
            print(str(e))
            traceback.print_exc(file=sys.stdout)

        print(blocks)

        variables = []
        for block in blocks:
            variables.append(self.convert_variable_to_json(block))
        return variables

    def convert_variable_to_json(self, block: SimpleBlock):
        if block.top_row == block.bottom_row:
            row_slice = IndexSlice()
            row_slice.idx = block.top_row
        else:
            row_slice = RangeSlice()
            row_slice.start = block.top_row
            row_slice.end = block.bottom_row
            row_slice.step = 1

        if block.left_col == block.right_col:
            col_slice = IndexSlice()
            col_slice.idx = block.left_col
        else:
            col_slice = RangeSlice()
            col_slice.start = block.left_col
            col_slice.end = block.right_col
            col_slice.step = 1

        slices = [row_slice, col_slice]

        location = Location()
        location.slices = slices
        location.resource_id = self.resource_id

        _json = Variable()
        _json.id = "test_id"  # TODO: give id to variable
        _json.location = location

        return _json
