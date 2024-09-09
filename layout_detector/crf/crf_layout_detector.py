from layout_detector.layout_detector import LayoutDetector
from layout_detector.crf.featurizer import Featurize
import numpy as np
import pickle
from config import config, get_full_path

from type.layout.basic_edge_type import BasicEdgeType
from type.layout.layout_graph import LayoutGraph
from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from typing import List
from type.block.simple_block import SimpleBlock


class CRFLayoutDetector(LayoutDetector):
    def __init__(self):
        layout_model_file = get_full_path(config['crf']['layout_detector_model_file'])
        with open(layout_model_file, 'rb') as infile:
            self.model = pickle.load(infile)

    def detect_layout(self, sheet: Sheet, tags: 'np.array[CellTypePMF]', blocks: List[SimpleBlock]) -> LayoutGraph:
        if len(blocks) == 2:
            ## TODO: Connect the two blocks?
            return LayoutGraph(blocks)

        for block in blocks:
            print(block)

        featurizer = Featurize([sheet], [tags], [blocks])
        X_graph, vertex_dict = np.array(featurizer.get_input_features())
        layout_prediction = self.model.predict(X_graph)[0]

        reverse_vertex_dict = dict()

        for k in vertex_dict[0]:
            v = vertex_dict[0][k]
            reverse_vertex_dict[v] = k

        # Convert predictions to layout graph
        layout_graph = LayoutGraph(blocks)
        for i in range(len(layout_prediction)):
            label = layout_prediction[i]
            if label != 0:  # 0 for null label
                label_name = BasicEdgeType.inv_edge_labels[label]
                v1, v2 = reverse_vertex_dict[i]
                layout_graph.add_edge(label_name, v1, v2)

        return layout_graph

