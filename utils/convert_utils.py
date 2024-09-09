from type.cell.semantic_cell_type import SemanticCellType
from type.block.function_block_type import FunctionBlockType
from type.block.simple_block import SimpleBlock
from type.cell.cell_type_pmf import CellTypePMF
from type.block.block_type_pmf import BlockTypePMF
from type.layout.layout_graph import LayoutGraph
from type.layout.basic_edge_type import BasicEdgeType
import numpy as np

def convert_str_id_cc(predictions):
    # convert cell types (from strings) to ids
    # input: a list where each item is a 2d list of cells types
    # output: a list where each item is a 2d list of ids (integers)
    results = []

    for idx, pred in enumerate(predictions):
        r, c = len(pred), len(pred[0])
        for i in range(r):
            for j in range(c):
                results.append(SemanticCellType.inverse_dict[pred[i][j]].id())

    return np.array(results)


def convert_str_np_cc(predictions):
    # convert cell types (from strings) to numpy CellTypePMF objects
    # input: a list where each item is a 2d list of cell types.
    # output: a list where each item is a 2d numpy array
    results = []

    for idx, pred in enumerate(predictions):
        r, c = len(pred), len(pred[0])
        ret = np.empty((r, c), dtype=CellTypePMF)

        for i in range(r):
            for j in range(c):
                type_class = {SemanticCellType.inverse_dict[pred[i][j]]: 1.0}
                ret[i][j] = CellTypePMF(type_class)

        results.append(ret)
    return results

def convert_blk_blkobj(block_list):
    # convert blocks (from tuples) to block object
    # input: a list where each item is a list of tuples
    # output: a list where each item is a list of block objects
    results = []

    for blks in block_list:
        results.append([])
        for blk in blks:
            (lx, ly, rx, ry, typ) = blk

            temp = SimpleBlock(BlockTypePMF(
						{FunctionBlockType.inverse_dict[typ]: 1.0}
						),
					ly, ry, lx, rx)
            results[-1].append(temp)
    return results


def convert_blk_celltype_id(block_list, sheets):
    # convert blocks (from tuples) to cells (2d numpy array)
    # input: a list where each item is a list of tuples, and a list of sheets
    # output: a 1d array (flattened) of cell type ids (integers)
    results = []

    for idx, blocks in enumerate(block_list):
        r, c = sheets[idx].values.shape
        labs = np.zeros((r, c))
        labs.fill(-1)
        for blk in blocks:
            (lx, ly, rx, ry, typ) = blk
            for i in range(lx, rx + 1):
                for j in range(ly, ry + 1):
                    labs[i][j] = FunctionBlockType.inverse_dict[typ].id()
        results += labs.flatten().tolist()

    return results

def convert_blkobj_celltype_id(block_list, sheets):
    # convert block objects to cells (2d numpy array)
    # input: a list where each item is a list of block objects, and a list of sheets
    # output: a 1d array (flattened) of cell type ids (integers)
    results = []

    for idx, blocks in enumerate(block_list):
        r, c = sheets[idx].values.shape
        labs = np.zeros((r, c))
        labs.fill(-1)
        for blk in blocks:
            lx, ly, rx, ry = blk.top_row, blk.left_col, blk.bottom_row, blk.right_col
            for i in range(lx, rx + 1):
                for j in range(ly, ry + 1):
                    labs[i][j] = blk.block_type.get_best_type().id()
        results += labs.flatten().tolist()
    return results

def convert_lst_graphobj(edge_list, block_list):
    # convert edges to layout graph objects
    # input: a list where each item is a list of tuples, and a list of lists of blocks
    # output: a list of layout graphs
    results = []

    for idx, edges in enumerate(edge_list):
        g = LayoutGraph(block_list[idx])
        #print(len(block_list[idx]))

        for edge in edges:
            #print(edge)
            typ = BasicEdgeType.str_to_edge_type[edge[-1]]
            g.add_edge(typ, edge[0], edge[1])

        results.append(g)
    return results
