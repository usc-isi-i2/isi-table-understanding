from annotator.abstract_annotator import AbstractAnnotator
from type.block.block import Block
from type.layout.layout_graph import LayoutGraph
import yaml
from typing import List
from type.block.simple_block import SimpleBlock


class YAMLAnnotator(AbstractAnnotator):
    def __init__(self, file_type, version=1):
        self.annotation = dict()
        self.annotation['version'] = str(version)
        self.annotation['resources'] = file_type
        self.annotation['variables'] = dict()

        self.annotation['alignments'] = []
        self.annotation['preprocessing'] = []


    def add_layout(self, label, block):
        layout = dict()
        layout['ObservationData'] = "{}..{}, {}..{}".format(block.get_top_row(), block.get_bottom_row(),
                                        block.get_left_col(), block.get_right_col())

        self.annotation['variables'][label] = layout  # TODO: What if two blocks have the same label?

    def add_mapping(self, label1, block1: SimpleBlock, label2, block2: SimpleBlock):
        mapping_type = "dimension"

        mapping = dict()
        mapping['type'] = mapping_type

        mapped_dimension = -1
        if block1.are_blocks_vertical(block2):
            mapped_dimension = 1
        elif block1.are_blocks_horizontal(block2):
            mapped_dimension = 0

        mapping['value'] = "{}:{} <-> {}:{}".format(label1, mapped_dimension, label2, mapped_dimension)

        self.annotation['alignments'].append(mapping)

    def write_yaml(self, annotation: dict, outfile):
        with open(outfile, 'w') as out:
            yaml.dump(annotation, out, default_flow_style=False)
            print("Successfully written yaml output")

    def add_mappings(self, layout: LayoutGraph, block_labels: dict):
        for vertex_1 in range(len(layout.nodes)):
            for edge_num in range(len(layout.outEdges[vertex_1])):
                label, vertex_2 = layout.outEdges[vertex_1][edge_num]
                print("adding mapping from", vertex_1, "to ", vertex_2)
                self.add_mapping(block_labels[layout.nodes[vertex_1]], layout.nodes[vertex_1],
                                 block_labels[layout.nodes[vertex_2]], layout.nodes[vertex_2])

    def get_annotation(self, sheet_index, sheet, tags, blocks: List[SimpleBlock], layout: LayoutGraph) -> dict:
        block_labels = dict()
        label_count = dict()

        if blocks:
            for block in blocks:

                block_type = block.get_block_type().get_best_type()
                if block_type in label_count:
                    label_num = label_count[block_type]
                    label_count[block_type] += 1
                else:
                    label_num = 0
                    label_count[block_type] = 1

                block_labels[block] = block_type.str() + str(label_num)
                self.add_layout(block_labels[block], block)

        self.add_mappings(layout, block_labels)

        return self.annotation
