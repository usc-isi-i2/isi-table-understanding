from type.cell.semantic_cell_type import SemanticCellType
from type.cell.cell_type_pmf import CellTypePMF
from type.block.simple_block import SimpleBlock
from type.block.function_block_type import FunctionBlockType
from type.block.block_type_pmf import BlockTypePMF
from block_extractor.block_extractor import BlockExtractor
from block_extractor.block_extractor_v2 import BlockExtractorV2
from block_extractor.utils import *
from typing import List
from reader.sheet import Sheet
import numpy as np
import random
import heapq
import math

class DistFuncs:
    def __init__(self, emb, typ, c_fun, m_fun, s_fun):
        self.emb = emb
        self.typ = typ
        self.m_fun = m_fun
        self.c_fun = c_fun
        self.s_fun = s_fun

        self.r_n, self.c_n, self.e_n = emb.shape[0], emb.shape[1], emb.shape[2]
        self.row_dist_matrix = np.zeros((self.r_n-1, self.c_n))
        self.col_dist_matrix = np.zeros((self.r_n, self.c_n-1))
        self.row_tag_dist = np.ones((self.r_n-1, self.c_n))
        self.col_tag_dist = np.ones((self.r_n, self.c_n-1))

        self.row_dists = np.zeros((self.r_n-1, ))
        self.col_dists = np.zeros((self.c_n-1, ))

        if self.c_fun is not None:

            for i in range(self.r_n-1):
                self.row_dist_matrix[i] = self.c_fun(emb[i, :], emb[i+1, :])
                self.row_dists[i] = np.mean(self.row_dist_matrix[i])

            for j in range(self.c_n-1):
                self.col_dist_matrix[:, j] = self.c_fun(emb[:, j], emb[:, j+1])
                self.col_dists[j] = np.mean(self.col_dist_matrix[:, j])

    def get_representations(self, blk1, blk2):
        (lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2) = blk1, blk2
        emb1, emb2 = None, None

        emb1 = np.mean(self.emb[lx1:rx1+1, ly1:ry1+1], axis=(0, 1))
        emb2 = np.mean(self.emb[lx2:rx2+1, ly2:ry2+1], axis=(0, 1))

        return emb1, emb2

    def get_intra_sim(self, lx, ly, rx, ry):
        ## max
        flat = self.emb[lx:rx+1, ly:ry+1].reshape((-1, self.e_n))
        avg = np.mean(self.emb[lx:rx+1, ly:ry+1], axis=(0, 1)).reshape((1, -1))
        avg = np.repeat(avg, flat.shape[0], axis=0)
        dists = self.c_fun(flat, avg)
        return np.amax(dists)

    def get_distance_values(self, blk1, blk2, emb1, emb2):
        (lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2) = blk1, blk2
        min_lx, min_ly, max_rx, max_ry = min(lx1, lx2), min(ly1, ly2), max(rx1, rx2), max(ry1, ry2)

        if lx1 == rx2 + 1:
            global_d = self.row_dists[rx2]
            is_row = True
            cc_thre = np.mean(self.row_tag_dist[rx2, min_ly:max_ry+1])
            cc_thre += np.mean(self.row_tag_dist[rx2, :])
            dist = np.mean(self.row_dist_matrix[rx2:rx2+1, min_ly:max_ry+1])
        elif rx1 == lx2 - 1:
            global_d = self.row_dists[rx1]
            is_row = True
            cc_thre = np.mean(self.row_tag_dist[rx1, min_ly:max_ry+1])
            cc_thre += np.mean(self.row_tag_dist[rx1, :])
            dist = np.mean(self.row_dist_matrix[rx1:rx1+1, min_ly:max_ry+1])
        elif ly1 == ry2+1:
            global_d = self.col_dists[ry2]
            is_row = False
            cc_thre = np.mean(self.col_tag_dist[min_lx:max_rx+1, ry2])
            cc_thre += np.mean(self.col_tag_dist[:, ry2])
            dist = np.mean(self.col_dist_matrix[min_lx:max_rx+1, ry2:ry2+1])
        else:
            global_d = self.col_dists[ry1]
            is_row = False
            cc_thre = np.mean(self.col_tag_dist[min_lx:max_rx+1, ry1])
            cc_thre += np.mean(self.col_tag_dist[:, ry1])
            dist = np.mean(self.col_dist_matrix[min_lx:max_rx+1, ry1:ry1+1])

        return self.m_fun(emb1, emb2), dist, is_row, global_d, cc_thre

    def get_distance(self, blk1, blk2, is_max, compute_intra=True):
        is_valid, (lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2) = extend(blk1, blk2)

        if not is_valid:
            return None, None

        if not isinstance(blk1, tuple):
            blk1 = (blk1.top_row, blk1.left_col, blk1.bottom_row, blk1.right_col)
            blk2 = (blk2.top_row, blk2.left_col, blk2.bottom_row, blk2.right_col)

        emb1, emb2 = self.get_representations(blk1, blk2)

        dist, adj_dist, is_row, global_d, cc_thre = self.get_distance_values(blk1, blk2,
                                                                       emb1, emb2)
        min_lx, min_ly, max_rx, max_ry = min(lx1, lx2), min(ly1, ly2), max(rx1, rx2), max(ry1, ry2)

        if compute_intra:
            intra_sim = self.get_intra_sim(min_lx, min_ly, max_rx, max_ry)
        else:
            intra_sim = 0

        overall_dist = cc_thre * (global_d + intra_sim + dist)

        dist_wo_weight = adj_dist

        return overall_dist, dist_wo_weight, is_row, intra_sim

    def get_dists(self, blk_pairs):
        row_distances, col_distances = [], []

        for idx, (blk1, blk2) in enumerate(blk_pairs):
            for _t in [True]:
                dist, _, is_row, __ = self.get_distance(blk1, blk2, _t)

                if dist is None:
                    continue
                if is_row:
                    row_distances.append(dist)
                else:
                    col_distances.append(dist)
        return row_distances, col_distances

    def get_X_y(self, blks):
        sample_blk_pairs = sample_inner_pairs(blks)
        typ_dic = {}
        X, y = [], []
        for (_t, blk1, blk2) in sample_blk_pairs:
            (emb1, emb2) = self.get_representations(blk1, blk2)
            if _t not in typ_dic:
                typ_dic[_t] = []
            typ_dic[_t].append(emb1)
            typ_dic[_t].append(emb2)
        return typ_dic


class BlockExtractorHAC(BlockExtractor):

    def __init__(self, row_perc, col_perc, ct_weights, sample_num):
        self.row_perc = row_perc
        self.col_perc = col_perc
        self.ct_weights = ct_weights
        self.sample_num = sample_num

    def get_initial_dists(self, sheet, tags, dist_func, dist_heap):
        r, c = sheet.values.shape
        dist_dic = {}
        neighbor_dic = {}
        reverse_map = [[None for j in range(c)] for i in range(r)]
        valid_dist_heap = set()

        for i in range(r):
            for j in range(c):
                tup_list = set()
                reverse_map[i][j] = (i, j, i, j)
                if i == 0:
                    if j > 0:
                        tup_list.add((i, j-1))
                else:
                    if j > 0:
                        tup_list.add((i, j-1))

                    tup_list.add((i-1, j))

                for (lx1, ly1) in tup_list:
                    dist, _dist_wo, is_row, __ = dist_func.get_distance((lx1, ly1, lx1, ly1), (i, j, i, j), True)

                    dist_dic[((lx1, ly1, lx1, ly1), (i, j, i, j), True)] = (dist, is_row)
                    heapq.heappush(dist_heap, (dist, is_row, True, (lx1, ly1, lx1, ly1),
                                                    (i, j, i, j)))
                    valid_dist_heap.add(((lx1, ly1, lx1, ly1), (i, j, i, j)))

        return dist_dic, reverse_map, valid_dist_heap

    def get_all_neighbors(self, b, active_indices):
        (lx, ly, rx, ry) = b
        neighbors = set()

        if lx > 0:
            for jj in range(ly, ry+1):
                neighbors.add(active_indices[lx-1][jj])
        if rx+1 < len(active_indices):
            for jj in range(ly, ry+1):
                neighbors.add(active_indices[rx+1][jj])
        if ly > 0:
            for ii in range(lx, rx+1):
                neighbors.add(active_indices[ii][ly-1])
        if ry+1 < len(active_indices[0]):
            for ii in range(lx, rx+1):
                neighbors.add(active_indices[ii][ry+1])

        return neighbors

    def valid_max_merge(self, b1, b2, active_indices, reverse_map, c):
        lx, rx = min(b1[0], b2[0]), max(b1[2], b2[2])
        ly, ry = min(b1[1], b2[1]), max(b1[3], b2[3])
        is_max = True

        if ly > 0:
            eq = np.equal(active_indices[lx:rx+1, ly],
                                active_indices[lx:rx+1, ly-1],
                                dtype=int)
            if np.sum(eq) > 0:
                return False
        if ry < active_indices.shape[1]-1:
            eq = np.equal(active_indices[lx:rx+1, ry],
                            active_indices[lx:rx+1, ry+1],
                            dtype=int)
            if np.sum(eq) > 0:
                return False
        if lx > 0:
            eq = np.equal(active_indices[lx, ly:ry+1],
                            active_indices[lx-1, ly:ry+1],
                            dtype=int)
            if np.sum(eq) > 0:
                return False
        if rx < active_indices.shape[0]-1:
            eq = np.equal(active_indices[rx, ly:ry+1],
                            active_indices[rx+1, ly:ry+1],
                            dtype=int)
            if np.sum(eq) > 0:
                return False
        return True

    def revise_a_block_shrink(self, lx1, ly1, lx2, ly2, dic):
        b1 = dic[lx1][ly1]
        b2 = dic[lx2][ly2]
        add_pairs = {}
        overlap_area = None

        if row_adjacent(b1, b2):
            lx, rx = min(b1[0], b2[0]), max(b1[2], b2[2])
            ly, ry = max(b1[1], b2[1]), min(b1[3], b2[3])
            add_pairs[(lx, ly)] = (lx, ly, rx, ry)
            if b1[1] < ly:
                add_pairs[(b1[0], b1[1])] = (b1[0], b1[1], b1[2], ly-1)
            if b1[3] > ry:
                add_pairs[(b1[0], ry+1)] = (b1[0], ry+1, b1[2], b1[3])
            if b2[1] < ly:
                add_pairs[(b2[0], b2[1])] = (b2[0], b2[1], b2[2], ly-1)
            if b2[3] > ry:
                add_pairs[(b2[0], ry+1)] = (b2[0], ry+1, b2[2], b2[3])

            if b1[0] == lx:
                overlap_area = (b1[0], ly, b1[2], ry, "t")
            else:
                overlap_area = (b2[0], ly, b2[2], ry, "b")
        elif col_adjacent(b1, b2):
            lx, rx = max(b1[0], b2[0]), min(b1[2], b2[2])
            ly, ry = min(b1[1], b2[1]), max(b1[3], b2[3])

            add_pairs[(lx, ly)] = (lx, ly, rx, ry)
            if b1[0] < lx:
                add_pairs[(b1[0], b1[1])] = (b1[0], b1[1], lx-1, b1[3])
            if b1[2] > rx:
                add_pairs[(rx+1, b1[1])] = (rx+1, b1[1], b1[2], b1[3])
            if b2[0] < lx:
                add_pairs[(b2[0], b2[1])] = (b2[0], b2[1], lx-1, b2[3])
            if b2[2] > rx:
                add_pairs[(rx+1, b2[1])] = (rx+1, b2[1], b2[2], b2[3])

            if b1[1] == ly:
                overlap_area = (lx, b1[1], rx, b1[3], "l")
            else:
                overlap_area = (lx, b2[1], rx, b2[3], "r")

        return (lx, ly, rx, ry), add_pairs, overlap_area

    def revise_a_block(self, lx1, ly1, lx2, ly2, dic):
        b1 = dic[lx1][ly1]
        b2 = dic[lx2][ly2]
        lx, rx = min(b1[0], b2[0]), max(b1[2], b2[2])
        ly, ry = min(b1[1], b2[1]), max(b1[3], b2[3])
        add_pairs = {}
        add_pairs[(lx, ly)] = (lx, ly, rx, ry)

        return (lx, ly, rx, ry), add_pairs

    def select_a_pair(self, sheet, dist_heap, all_dist_dic, reverse_map,
            active_indices, dist_func, visited, valid_dist_heap):
        r, c = sheet.values.shape

        (lx1, ly1, lx2, ly2), (dist, is_row, is_max) = (None, None, None, None), (None, None, None)

        while len(dist_heap) > 0:
            (d, i_r, _max, (_lx, _ly, _rx, _ry), (_lx2, _ly2, _rx2, _ry2)) = heapq.heappop(dist_heap)

            valid_dist_heap.discard(((_lx, _ly, _rx, _ry), (_lx2, _ly2, _rx2, _ry2)))

            valid_dist_heap.discard(((_lx2, _ly2, _rx2, _ry2), (_lx, _ly, _rx, _ry)))

            if active_indices[_lx][_ly] != _lx * c + _ly:
                continue

            if active_indices[_lx2][_ly2] != _lx2 * c + _ly2:
                continue

            if reverse_map[_lx][_ly] != (_lx, _ly, _rx, _ry):
                continue

            if reverse_map[_lx2][_ly2] != (_lx2, _ly2, _rx2, _ry2):
                continue

            (lx1, ly1, lx2, ly2), (dist, is_row, is_max) = (_lx, _ly, _lx2, _ly2), (d, i_r, _max)
            break

        if (lx1 is None):
            return (False, None, None)
        if dist > self.thre:
            return (False, None, None)

        is_max = self.valid_max_merge(reverse_map[lx1][ly1], reverse_map[lx2][ly2],
                                        active_indices, reverse_map, c)
        if is_max:
            final_block, add_pairs = \
                self.revise_a_block(lx1, ly1, lx2, ly2, reverse_map)
        else:
            (_lx, _ly, _rx, _ry), (_lx2, _ly2, _rx2, _ry2) = reverse_map[lx1][ly1], reverse_map[lx2][ly2]
            if is_row and ((_ly < _ly2 and _ry2 < _ry) or (_ly2 < _ly and _ry < _ry2)):
                return (True, None, None)
            if (not is_row) and ((_lx < _lx2 and _rx2 < _rx) or (_lx2 < _lx and _rx < _rx2)):
                return (True, None, None)
            final_block, add_pairs, overlap_area = \
                self.revise_a_block_shrink(lx1, ly1, lx2, ly2, reverse_map)

            if final_block in visited:
                return (True, None, None)
            visited.add(final_block)

        for p in add_pairs:
            tup = add_pairs[p]
            _ix = tup[0] * c + tup[1]
            reverse_map[tup[0]][tup[1]] = tup
            active_indices[tup[0]:tup[2]+1, tup[1]:tup[3]+1] = _ix

        for p in add_pairs:
            tup = add_pairs[p]
            neighbors = self.get_all_neighbors(tup, active_indices)
            for n in neighbors:
                x, y = int(n / c), n % c
                v_max = True

                if (tup, reverse_map[x][y]) in valid_dist_heap:
                    continue
                if (reverse_map[x][y], tup) in valid_dist_heap:
                    continue

                if (tup, reverse_map[x][y], v_max) in all_dist_dic:
                    dist, is_row = all_dist_dic[(tup, reverse_map[x][y], v_max)]
                elif (reverse_map[x][y], tup, v_max) in all_dist_dic:
                    dist, is_row = all_dist_dic[(reverse_map[x][y], tup, v_max)]
                else:
                    dist, _dist_wo, is_row, i_s = dist_func.get_distance(tup, reverse_map[x][y], True)

                    all_dist_dic[(reverse_map[x][y], add_pairs[p], v_max)] = (dist, is_row)

                if dist > self.thre:
                    continue

                heapq.heappush(dist_heap, (dist, is_row, v_max,
                                           reverse_map[x][y], add_pairs[p]
                                         ))

        return (True, reverse_map[lx1][ly1], reverse_map[lx2][ly2])

    def update_dist_func(self, tags, dist_func):

        for i in range(len(tags)):
            for j in range(len(tags[i])):
                if i+1 < len(tags):
                    if tags[i][j] < tags[i+1][j]:
                        if (tags[i][j], tags[i+1][j], True) in self.ct_weights:
                            dist_func.row_tag_dist[i][j] = self.ct_weights[(tags[i][j], tags[i+1][j], True)]
                    else:
                        if (tags[i+1][j], tags[i][j], True) in self.ct_weights:
                            dist_func.row_tag_dist[i][j] = self.ct_weights[(tags[i+1][j], tags[i][j], True)]

                if j+1 < len(tags[i]):
                    if tags[i][j] < tags[i][j+1]:
                        if (tags[i][j], tags[i][j+1], False) in self.ct_weights:
                            dist_func.col_tag_dist[i][j] = self.ct_weights[(tags[i][j], tags[i][j+1], False)]
                    else:
                        if (tags[i][j+1], tags[i][j], False) in self.ct_weights:
                            dist_func.col_tag_dist[i][j] = self.ct_weights[(tags[i][j+1], tags[i][j], False)]

    def set_global_threshold(self, sheet, dist_func):
        sample_blks = sample_block_pairs_v2(sheet, self.sample_num)
        sample_rows, sample_cols = dist_func.get_dists(sample_blks)

        sample_all = sample_rows + sample_cols
        if len(sample_all) > 0:
            self.thre = sorted(sample_all)[min(len(sample_all)-1, int(self.row_perc*len(sample_all)))]
        else:
            self.thre = float("inf")

    def extract_blocks(self, sheet: Sheet, tags, dist_func) -> List[SimpleBlock]:

        def convert_ct(typ):

            cell_class_dict = {
                SemanticCellType.inverse_dict[typ]: 1.0
            }
            return CellTypePMF(cell_class_dict)

        tags = [[convert_ct(t.get_best_type().str()) for t in tag] for tag in tags]

        tags = [[t.get_best_type().str()
                    for t in tag] for tag in tags]

        self.update_dist_func(tags, dist_func)

        self.set_global_threshold(sheet, dist_func)

        dist_heap = []

        all_dist_dic, reverse_map,valid_dist_heap = self.get_initial_dists(sheet, tags,
                                                                            dist_func, dist_heap)

        invalid_set = set()
        visited = set()
        r, c = sheet.values.shape

        active_indices = np.array([[_x*c+_y for _y in range(c)] for _x in range(r)])

        while True:
            best_pair = self.select_a_pair(sheet, dist_heap, all_dist_dic, reverse_map,
                                           active_indices, dist_func, visited, valid_dist_heap)
            if not best_pair[0]:
                break

        blocks = []

        blocks_set = set([reverse_map[int(_ / c)][_ % c] for item in active_indices for _ in item])

        for (lx, ly, rx, ry) in blocks_set:

            pmf = BlockTypePMF(
                    {FunctionBlockType.inverse_dict["data"]: 1.0}
                    )

            blk = SimpleBlock(pmf, ly, ry, lx, rx)
            blocks.append(blk)

        return blocks
