import os
import numpy as np
from layout_detector.random_forest.featurize import *
from joblib import dump, load
from layout_detector.layout_detector import LayoutDetector
from type.layout.layout_graph import LayoutGraph
from type.block.simple_block import SimpleBlock
from type.layout.basic_edge_type import BasicEdgeType
from reader.sheet import Sheet
from typing import List
import pandas as pd
import itertools

class LayoutDetectorRF(LayoutDetector):

    def __init__(self, model_file):

        self.model = load(model_file)

    def __predict_wrapper(self, pred, pairs, blocks):

        graph = LayoutGraph(blocks)

        for idx, (i, j) in enumerate(pairs):

            graph.add_edge(BasicEdgeType.inv_edge_labels[pred[idx]], i, j)

        return graph

    def detect_layout(self, sheet: Sheet, tags: 'np.array[CellTypePMF]', blocks: List[SimpleBlock]):

        indices = [_ for _ in range(len(blocks))]

        feats = []

        pairs = []

        for (i, j) in itertools.combinations(indices, 2):

            feats.append(block_relation_feats(blocks[i], blocks[j]))

            pairs.append((i, j))

        if len(feats) != 0:
            pred = self.model.predict(feats)
        else:
            pred = []

        layout_graphs = self.__predict_wrapper(pred, pairs, blocks)

        return layout_graphs

    def detect_layout_all_tables(self, sheet, tags, blocks):

        return [self.detect_layout(sheet[i], tags[i], blocks[i])
                    for i in range(len(sheet))]
