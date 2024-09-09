from type.block.simple_block import SimpleBlock
from type.layout.layout_graph import LayoutGraph
from type.layout.basic_edge_type import BasicEdgeType
from layout_detector.random_forest.featurize import *
from typing import List
from reader.sheet import Sheet
import numpy as np

def get_input_features_for_table(blocks):
    edge_map = []
    edge_features = []
    feature_map = []
    linked_blocks = []

    for i in range(len(blocks)):
        for j in range(len(blocks)):
            if i != j:
                feature_map.append(block_relation_feats(blocks[i], blocks[j]))
                linked_blocks.append([i, j])

    for x1 in range(len(linked_blocks)):
        for x2 in range(len(linked_blocks)):
            i1, j1 = linked_blocks[x1]
            i2, j2 = linked_blocks[x2]

            if (i1, j1) == (i2, j2):
                continue
            #elif (i1, j1) == (j2, i2):
            #    continue
            elif (i1 != i2 and j1 != j2) and (i1 != j2 and j1 != i2):
                continue
            else:
                edge_map.append([x1, x2])
                edge_feature = feature_map[x1] + feature_map[x2]
                edge_features.append(np.array(edge_feature))

    return np.array(feature_map), np.array(edge_map), np.array(edge_features), linked_blocks


def get_label_map(layout_graph):
    blocks = layout_graph.nodes
    label_dict = {}
    labels = []

    for j in range(len(layout_graph.outEdges)):
        v1 = j
        for _type, v2 in layout_graph.outEdges[v1]:
            label_dict[(v1, v2)] = _type.id()

    for i in range(len(blocks)):
        for j in range(len(blocks)):
            if i == j:
                continue
            if (i, j) in label_dict:
                labels.append(label_dict[(i, j)])
            else:
                labels.append(BasicEdgeType.str_to_edge_type["empty"].id())
    return np.array(labels)
