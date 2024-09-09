from layout_detector.layout_detector import LayoutDetector
from type.layout.layout_graph import LayoutGraph

from reader.sheet import Sheet
from type.cell.cell_type_pmf import CellTypePMF
from typing import List
from type.block.simple_block import SimpleBlock
from type.block import block_type
import numpy as np
from type.block.basic_block_type import BasicBlockType
from type.layout.basic_edge_type import BasicEdgeType

# """
# Assigns each DATA block to nearest META and DATE blocks as long as they are aligned.
# Assigns each DATE block and META block to nearest DATA block as long as they are aligned.
# """

"""
Creates an edge between each VALUE block and all ATTRIBUTE blocks.
"""
class ExampleLayoutDetector(LayoutDetector):
    def neighbors(self, idx, blocks) -> set:
        n = set()
        vertex = blocks[idx]

        if vertex.get_block_type().get_best_type() == BasicBlockType.VALUE:
            for idx, block in enumerate(blocks):
                if block.get_block_type().get_best_type() == BasicBlockType.ATTRIBUTE:
                    n.add(idx)

        return n

    """
    Returns an adjacency list with block_idx as vertex
    """
    def detect_layout(self, sheet: Sheet, tags: 'np.array[CellTypePMF]', blocks: List[SimpleBlock]):
        layout_graph = LayoutGraph(blocks)

        for i in range(len(blocks)):
            neighbor_set = self.neighbors(i, blocks)
            for vertex in neighbor_set:
                print("Edge created from {} to {}".format(vertex, i))
                layout_graph.add_edge(BasicEdgeType.ATTRIBUTE, vertex, i)

        return layout_graph
