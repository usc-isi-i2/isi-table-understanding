"""
Experimental code. Subject to change
"""


from type.block.simple_block import SimpleBlock
# from block_extractor.new_block_types import block_map
from type.block.basic_block_type import BasicBlockType
from type.layout.layout_graph import LayoutGraph
from typing import List
from reader.sheet import Sheet
import numpy as np


class Featurize:
    def __init__(self, sheetList: List, tagsList: List, blocksList: List):
        self.sheetList = sheetList
        self.tagsList = tagsList
        self.blocksList = blocksList
        self.vertexDict = dict()

    def get_input_features_for_table(self, table_num, sheet: Sheet, tags: 'np.array[CellClass]',
                                     blocks: List[SimpleBlock]):

        edge_map = []
        edge_features = []
        feature_map = []
        linked_blocks = []
        self.vertexDict[table_num] = dict()

        # List all nodes in the CRF
        # Assuming edges in both directions exist
        vertex_num = 0
        for i in range(len(blocks)):
            for j in range(len(blocks)):
                # Node (i, j) in CRF
                if i != j:
                    # edge_map.append([i, j])
                    feature_map.append(self.get_block_relation_features(blocks[i], blocks[j]))
                    linked_blocks.append([i, j])

                    # Create a map from (block_a, block_b) pair to vertex_id
                    # Remember all vertex id assignments
                    self.vertexDict[table_num][(i, j)] = vertex_num
                    vertex_num += 1

        # print(self.vertexDict[table_num])

        # List all edges in CRF
        # An edge in the CRF would have a common block
        for x1 in range(len(linked_blocks)):
            for x2 in range(len(linked_blocks)):
                i1, j1 = linked_blocks[x1]
                i2, j2 = linked_blocks[x2]

                vertex_1 = self.vertexDict[table_num][(i1, j1)]
                vertex_2 = self.vertexDict[table_num][(i2, j2)]

                if (i1, j1) == (i2, j2):
                    pass  # same link
                elif (i1, j1) == (j2, i2):
                    # opposite links! what to do here?
                    # TODO: add features from both blocks
                    pass
                elif (i1 != i2 and j1 != j2) and (i1 != j2 and j1 != i2):
                    # links have no common block
                    pass
                # elif (i1 == j1) or (i2 == j2):
                #     pass
                else:
                    # print(i1, j1, i2, j2)
                    edge_map.append([vertex_1, vertex_2])
                    edge_feature = feature_map[vertex_1] + feature_map[vertex_2]
                    edge_features.append(np.array(edge_feature))
                    # TODO: also add edge features here

        return np.array(feature_map), np.array(edge_map), np.array(edge_features)

    def get_input_features(self):

        X_graph = []

        for k in range(len(self.sheetList)):
            sheet = self.sheetList[k]
            tags = self.tagsList[k]
            blocks = self.blocksList[k]

            feature_map, edge_map, edge_features = self.get_input_features_for_table(k, sheet, tags, blocks)
            X_graph.append((feature_map, edge_map, edge_features))

        return X_graph, self.vertexDict

    def get_label_map(self, layoutList: List[LayoutGraph]):
        labelsList = []
        # convert labels to keys
        for i in range(len(layoutList)):
            vertexDict = self.vertexDict[i]
            layout = layoutList[i]

            # For each link, what is the label?
            label_size = len(vertexDict)
            # print("Number of labels is {}".format(label_size))

            labelsList.append(np.zeros(label_size, dtype=int))

            for j in range(len(layout.outEdges)):
                v1 = j
                for _type, v2 in layout.outEdges[v1]:
                    vertex_num = vertexDict[(v1, v2)]
                    labelsList[i][vertex_num] = _type.id()
                    # print("({}, {}) is assigned type: {}".format(v1, v2, type))

            # print(labelsList[i])

        return np.array(labelsList)


    def get_block_relation_features(self, block1: SimpleBlock, block2: SimpleBlock):
        features = []

        # Add block 1 type
        features.extend([0] * BasicBlockType.block_type_count())
        features[block1.get_block_type().get_best_type().id()] = 1

        # Add block 2 type
        features.extend([0] * BasicBlockType.block_type_count())
        features[block2.get_block_type().get_best_type().id() + BasicBlockType.block_type_count()] = 1

        # Are 2 blocks adjacent
        features.append(block1.is_adjacent(block2))

        # Are 2 blocks separated by 1 row/column
        features.append(block1.are_blocks_within_x_row_or_column(2, block2))

        # Are 2 blocks separated by 4 rows/columns
        features.append(block1.are_blocks_within_x_row_or_column(5, block2))

        # Are 2 blocks horizontal
        features.append(block1.are_blocks_horizontal(block2))

        # Are 2 blocks vertical
        features.append(block1.are_blocks_vertical(block2))

        # Do the blocks have a block in between # cannot compute with this input

        # TODO: Does the block have any adjacent blocks? Important?

        return features
