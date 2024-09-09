import pickle
from joblib import dump, load
import numpy as np
from layout_detector.crf.featurizer_v2 import *
from reader.sheet import Sheet
from type.layout.basic_edge_type import BasicEdgeType
from layout_detector.layout_detector import LayoutDetector
from type.block.simple_block import SimpleBlock
from typing import List

class LayoutDetectorCRF(LayoutDetector):
    def __init__(self, crf_model_file):
        self.model = load(crf_model_file)

    def __predict_wrapper(self, pred, blocks, linked_list):

        layout_graph = LayoutGraph(blocks)

        for idx, (p1, p2) in enumerate(linked_list):

            layout_graph.add_edge(BasicEdgeType.inv_edge_labels[pred[idx]],
                                  p1, p2)

        return layout_graph

    def detect_layout(self, sheet: Sheet, tags: 'np.array[CellTypePMF]', blocks: List[SimpleBlock]):
        feats = get_input_features_for_table(blocks)
        if len(feats[-1]) == 0:
            print("len 0", feats)
            ret = LayoutGraph(blocks)
        else:
            predictions = self.model.predict([(feats[0], feats[1], feats[2])])[0]

            ret = self.__predict_wrapper(predictions, blocks, feats[3])

        return ret

    def detect_layout_all_tables(self, sheet, tags, blocks):
        """
        feats = []
        linked_list = []
        for b in blocks:
            temp_feat = get_input_features_for_table(b)
            feats.append((temp_feat[0], temp_feat[1], temp_feat[2]))
            linked_list.append(temp_feat[3])

        predictions = self.model.predict(feats)

        all_tags = []
        for i in range(len(predictions)):
            tags = self.__predict_wrapper(predictions[i], blocks[i], linked_list[i])
            all_tags.append(tags)

        return all_tags
        """
        return [self.detect_layout(sheet[i], tags[i], blocks[i]) for i in range(len(sheet))]
