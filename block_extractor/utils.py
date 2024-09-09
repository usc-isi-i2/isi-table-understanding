import random
import numpy as np
from type.block.block_type_pmf import BlockTypePMF
from type.block.simple_block import SimpleBlock
from type.block.function_block_type import FunctionBlockType
from sklearn.metrics.pairwise import paired_distances

def remove_white_right(truth, lx, rx, ly, ry):
    while ry >= ly:
        can_skip = True
        for i in range(lx, rx + 1):
            if truth[i][ry] != -1:
                can_skip = False
                break
        if not can_skip:
            break
        ry -= 1
    return ry

def remove_white_bottom(truth, lx, rx, ly, ry):
    while rx >= lx:
        can_skip = True
        for i in range(ly, ry + 1):
            if truth[rx][i] != -1:
                can_skip = False
                break
        if not can_skip:
            break
        rx -= 1
    return rx

def remove_white_left(truth, lx, rx, ly, ry):
    while ly <= ry:
        can_skip = True
        for i in range(lx, rx + 1):
            if truth[i][ly] != -1:
                can_skip = False
                break
        if not can_skip:
            break
        ly += 1
    return ly

def remove_white_top(truth, lx, rx, ly, ry):
    while lx <= rx:
        can_skip = True
        for i in range(ly, ry + 1):
            if truth[lx][i] != -1:
                can_skip = False
                break
        if not can_skip:
            break
        lx += 1
    return lx

def row_adjacent(blk1, blk2):
    assert len(blk1) == 4 and len(blk2) == 4

    if blk1[0] == blk2[2] + 1 or blk1[2] == blk2[0] - 1:
        if blk1[1] <= blk2[3] and blk1[3] >= blk2[1]:
            return True
        else:
            return False
    else:
        return False

def col_adjacent(blk1, blk2):
    assert len(blk1) == 4 and len(blk2) == 4

    if blk1[1] == blk2[3] + 1 or blk1[3] == blk2[1] - 1:
        if blk1[0] <= blk2[2] and blk1[2] >= blk2[0]:
            return True
        else:
            return False
    else:
        return False

def get_block_indices(blk):
    if isinstance(blk, tuple):
        lx, ly, rx, ry = blk
    else:
        lx, ly, rx, ry = blk.top_row, blk.left_col, blk.bottom_row, blk.right_col
    return lx, ly, rx, ry

def extend(blk1, blk2):
    lx1, ly1, rx1, ry1 = get_block_indices(blk1)
    lx2, ly2, rx2, ry2 = get_block_indices(blk2)

    min_lx, min_ly, max_rx, max_ry = min(lx1, lx2), min(ly1, ly2), max(rx1, rx2), max(ry1, ry2)

    if row_adjacent((lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2)):
        return True, (lx1, min_ly, rx1, max_ry), (lx2, min_ly, rx2, max_ry)
    elif col_adjacent((lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2)):
        return True, (min_lx, ly1, max_rx, ry1), (min_lx, ly2, max_rx, ry2)
    else:
        return False, (lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2)

def shrink(blk1, blk2):
    lx1, ly1, rx1, ry1 = get_block_indices(blk1)
    lx2, ly2, rx2, ry2 = get_block_indices(blk2)

    max_lx, max_ly, min_rx, min_ry = max(lx1, lx2), max(ly1, ly2), min(rx1, rx2), min(ry1, ry2)

    if row_adjacent((lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2)):
        return True, (lx1, max_ly, rx1, min_ry), (lx2, max_ly, rx2, min_ry)
    elif col_adjacent((lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2)):
        return True, (max_lx, ly1, min_rx, ry1), (max_lx, ly2, min_rx, ry2)
    else:
        return False, (lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2)

def sample_inner_pairs(blks, k=30):
    #random.seed(0)
    blk_pairs = set()

    for blk in blks:
        lx, ly, rx, ry = blk.top_row, blk.left_col, blk.bottom_row, blk.right_col
        typ = blk.block_type.get_best_type().str()

        for i in range(k):
            #_v = random.random()
            if ly != ry:
                v = random.choice([_ for _ in range(ly, ry)])
                blk_pairs.add((typ, (lx, ly, rx, v), (lx, v+1, rx, ry)))
            if lx != rx:
                v = random.choice([_ for _ in range(lx, rx)])
                blk_pairs.add((typ, (lx, ly, v, ry), (v+1, ly, rx, ry)))
    return list(sorted(blk_pairs))

def sample_inner_pairs_wo_type(blks, k=3):
    blk_pairs = set()

    for blk in blks:
        lx, ly, rx, ry = blk.top_row, blk.left_col, blk.bottom_row, blk.right_col
        typ = blk.block_type.get_best_type().str()

        for i in range(k):
            if ly != ry:
                v = random.choice([_ for _ in range(ly, ry)])
                blk_pairs.add(((lx, ly, rx, v), (lx, v+1, rx, ry)))
            if lx != rx:
                v = random.choice([_ for _ in range(lx, rx)])
                blk_pairs.add(((lx, ly, v, ry), (v+1, ly, rx, ry)))
    return blk_pairs

def sample_block_pairs(sheet, num):
    r, c = sheet.values.shape
    blocks = set()
    #e_num = max(1, int(num / (r + c)))
    e_num = max(10, int(num / (r + c)))

    for i in range(r):
        for n in range(e_num):
            lx = i
            ly = random.choice([_ for _ in range(c)])
            rx = random.choice([_ for _ in range(lx, r)])
            ry = random.choice([_ for _ in range(ly, c)])
            assert rx >= lx and ry >= ly
            pmf = BlockTypePMF(
                        {FunctionBlockType.inverse_dict["data"]: 1.0}
                        )

            blk = SimpleBlock(pmf, ly, ry, lx, rx)

            if lx > 0:
                rx2 = lx - 1
                ly2 = random.choice([_ for _ in range(ry+1)])
                ry2 = random.choice([_ for _ in range(max(ly, ly2), c)])
                lx2 = random.choice([_ for _ in range(rx2+1)])
                assert rx2 >= lx2 and ry2 >= ly2
                blk2 = SimpleBlock(pmf, ly2, ry2, lx2, rx2)
                blocks.add((blk, blk2))
                #print("add a block")

    for j in range(c):
        for n in range(e_num):
            lx = random.choice([_ for _ in range(r)])
            ly = j
            rx = random.choice([_ for _ in range(lx, r)])
            ry = random.choice([_ for _ in range(ly, c)])
            assert rx >= lx and ry >= ly
            pmf = BlockTypePMF(
                        {FunctionBlockType.inverse_dict["data"]: 1.0}
                        )

            blk = SimpleBlock(pmf, ly, ry, lx, rx)

            if ly > 0:
                ry2 = ly - 1
                lx2 = random.choice([_ for _ in range(rx+1)])
                rx2 = random.choice([_ for _ in range(max(lx, lx2), r)])
                ly2 = random.choice([_ for _ in range(ry2+1)])
                assert rx2 >= lx2 and ry2 >= ly2
                blk2 = SimpleBlock(pmf, ly2, ry2, lx2, rx2)
                blocks.add((blk, blk2))
                #print("add a block")

    return blocks


def sample_block_pairs_v2(sheet, num):
    random.seed(0)
    r, c = sheet.values.shape
    blocks = set()
    visited = set()

    for _ in range(num):
        lx = random.choice([_ for _ in range(r)])
        ly = random.choice([_ for _ in range(c)])
        rx = random.choice([_ for _ in range(lx, r)])
        ry = random.choice([_ for _ in range(ly, c)])

        assert rx >= lx and ry >= ly
        pmf = BlockTypePMF(
            {FunctionBlockType.inverse_dict["data"]: 1.0}
                    )

        blk = SimpleBlock(pmf, ly, ry, lx, rx)

        if lx > 0:
            rx2 = lx - 1
            ly2 = random.choice([_ for _ in range(ry+1)])
            ry2 = random.choice([_ for _ in range(max(ly, ly2), c)])
            lx2 = random.choice([_ for _ in range(rx2+1)])
            assert rx2 >= lx2 and ry2 >= ly2
            blk2 = SimpleBlock(pmf, ly2, ry2, lx2, rx2)
            if (lx, ly, rx, ry, lx2, ly2, rx2, ry2) not in visited:
                blocks.add((blk, blk2))
                visited.add((lx, ly, rx, ry, lx2, ly2, rx2, ry2))
            #print("add a block")

        if ly > 0:
            ry2 = ly - 1
            lx2 = random.choice([_ for _ in range(rx+1)])
            rx2 = random.choice([_ for _ in range(max(lx, lx2), r)])
            ly2 = random.choice([_ for _ in range(ry2+1)])
            assert rx2 >= lx2 and ry2 >= ly2
            blk2 = SimpleBlock(pmf, ly2, ry2, lx2, rx2)
            if (lx, ly, rx, ry, lx2, ly2, rx2, ry2) not in visited:
                blocks.add((blk, blk2))
                visited.add((lx, ly, rx, ry, lx2, ly2, rx2, ry2))

    return blocks

def sample_block_pairs_v3(sheet, num):
    random.seed(0)
    r, c = sheet.values.shape
    blocks = set()
    visited = set()

    for _ in range(num):
        lx = random.choice([_ for _ in range(r)])
        ly = random.choice([_ for _ in range(c)])
        rx = random.choice([_ for _ in range(lx, r)])
        ry = random.choice([_ for _ in range(ly, c)])

        assert rx >= lx and ry >= ly
        pmf = BlockTypePMF(
            {FunctionBlockType.inverse_dict["data"]: 1.0}
                    )

        if rx > lx:
            mid = random.choice([_ for _ in range(lx, rx)])
            blk1 = SimpleBlock(pmf, ly, ry, lx, mid)
            blk2 = SimpleBlock(pmf, ly, ry, mid+1, rx)

            if (lx, ly, mid, ry, mid+1, ly, rx, ry) not in visited:
                blocks.add((blk1, blk2))
                visited.add((lx, ly, mid, ry, mid+1, ly, rx, ry))
        if ry > ly:
             mid = random.choice([_ for _ in range(ly, ry)])
             blk1 = SimpleBlock(pmf, ly, mid, lx, rx)
             blk2 = SimpleBlock(pmf, mid+1, ry, lx, rx)

             if (lx, mid, rx, ry, lx, mid+1, rx, ry) not in visited:
                 blocks.add((blk1, blk2))
                 visited.add((lx, mid, rx, ry, lx, mid+1, rx, ry))

    return blocks

def sample_blocks_v3(sheet, num):
    r, c = sheet.values.shape
    blocks = set()
    e_num = max(1, int(num / (r + c)))
    random.seed(0)

    for i in range(r):
        for n in range(e_num):
            lx = i
            ly = random.choice([_ for _ in range(c)])
            rx = random.choice([_ for _ in range(lx, r)])
            ry = random.choice([_ for _ in range(ly, c)])
            assert rx >= lx and ry >= ly
            pmf = BlockTypePMF(
                        {FunctionBlockType.inverse_dict["data"]: 1.0}
                        )

            blk = SimpleBlock(pmf, ly, ry, lx, rx)
            blocks.add(blk)

            if lx > 0:
                rx2 = lx - 1
                ly2 = random.choice([_ for _ in range(ry+1)])
                ry2 = random.choice([_ for _ in range(max(ly, ly2), c)])
                lx2 = random.choice([_ for _ in range(rx2+1)])
                assert rx2 >= lx2 and ry2 >= ly2
                blk = SimpleBlock(pmf, ly2, ry2, lx2, rx2)
                blocks.add(blk)

    for j in range(c):
        for n in range(e_num):
            lx = random.choice([_ for _ in range(r)])
            ly = j
            rx = random.choice([_ for _ in range(lx, r)])
            ry = random.choice([_ for _ in range(ly, c)])
            assert rx >= lx and ry >= ly
            pmf = BlockTypePMF(
                        {FunctionBlockType.inverse_dict["data"]: 1.0}
                        )

            blk = SimpleBlock(pmf, ly, ry, lx, rx)
            blocks.add(blk)

            if ly > 0:
                ry2 = ly - 1
                lx2 = random.choice([_ for _ in range(rx+1)])
                rx2 = random.choice([_ for _ in range(max(lx, lx2), r)])
                ly2 = random.choice([_ for _ in range(ry2+1)])
                assert rx2 >= lx2 and ry2 >= ly2
                blk = SimpleBlock(pmf, ly2, ry2, lx2, rx2)
                blocks.add(blk)

    return blocks

"""
def get_neighboring_distance(tab_emb, m_fun):
    # global info
    row_dist = []
    col_dist = []
    for i in range(tab_emb.shape[0] - 1):
        adj1 = np.mean(tab_emb[i:i+1, :], axis=(0, 1))
        adj2 = np.mean(tab_emb[i+1:i+2, :], axis=(0, 1))
        row_dist.append(m_fun(adj1, adj2))
    for j in range(tab_emb.shape[1] - 1):
        adj1 = np.mean(tab_emb[:, j:j+1], axis=(0, 1))
        adj2 = np.mean(tab_emb[:, j+1:j+2], axis=(0, 1))
        col_dist.append(m_fun(adj1, adj2))
    return np.array(row_dist), np.array(col_dist)
"""

def get_neighboring_distance(tab_emb, metric):
    row_dist = []
    col_dist = []
    for i in range(tab_emb.shape[0] - 1):
        temp = paired_distances(tab_emb[i, :], tab_emb[i+1, :], metric=metric)
        row_dist.append(sum(temp) / len(temp))
    for j in range(tab_emb.shape[1] - 1):
        temp = paired_distances(tab_emb[:, j], tab_emb[:, j+1], metric=metric)
        col_dist.append(sum(temp) / len(temp))
    return np.array(row_dist), np.array(col_dist)

def temp_convert_cc(lab):
    #if lab in ["nominal", "cardinal", "ordinal"]:
    #    lab = "number"
    #if lab in ["person", "organization", "location"]:
    #    lab = "string"
    return lab

def get_cc_blocks(sheet, celltypes):
    blk_pairs = set()
    r, c = sheet.values.shape
    for i in range(r):
        for j in range(c):
            if j+1 < c:
                blk_pairs.add(((i, j, i, j), (i, j+1, i, j+1),
                        (temp_convert_cc(celltypes[i][j].get_best_type().str()),
                        temp_convert_cc(celltypes[i][j+1].get_best_type().str()))))
            if i+1 < r:
                blk_pairs.add(((i, j, i, j), (i+1, j, i+1, j),
                        (temp_convert_cc(celltypes[i][j].get_best_type().str()),
                        temp_convert_cc(celltypes[i+1][j].get_best_type().str()))))

    return blk_pairs


def sample_cc_blocks(sheet, blks, num=50):
    blk_pairs = set()
    random.seed(0)
    r, c = sheet.values.shape
    #print([str(_) for _ in blks])
    for blk in blks:
        lx, ly, rx, ry = blk.top_row, blk.left_col, blk.bottom_row, blk.right_col
        typ = blk.block_type.get_best_type().str()
        #for _i in range(min(rx-lx, 5)):
        if lx != rx:
            for _i in range(num):
                lx2 = random.choice([_ for _ in range(lx, rx)])
                _lx1 = random.choice([_ for _ in range(lx2+1)])
                _rx2 = random.choice([_ for _ in range(lx2+1, r)])

                blk_pairs.add(((_lx1, ly, lx2, ry), (lx2+1, ly, _rx2, ry), (typ, typ)))
        #for _j in range(min(ry-ly, 5)):
        if ly != ry:
            for _j in range(num):
                ly2 = random.choice([_ for _ in range(ly, ry)])
                _ly1 = random.choice([_ for _ in range(ly2+1)])
                _ry2 = random.choice([_ for _ in range(ly2+1, c)])
                blk_pairs.add(((lx, _ly1, rx, ly2), (lx, ly2+1, rx, _ry2), (typ, typ)))

    for _i, b1 in enumerate(blks):
        typ1 = b1.block_type.get_best_type().str()
        #print(_i)
        for _j, b2 in enumerate(blks):
            if _j <= _i:
                continue

            typ2 = b2.block_type.get_best_type().str()

            v,(lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2) = shrink(b1, b2)

            if not v:
                #print("not valid", str(b1), str(b2))
                continue
            #print("valid", str(b1), str(b2), (lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2))
            if row_adjacent((lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2)):
                #for ii in range(min(max(rx1-lx1+1, rx2-lx2+1), 5)):
                for ii in range(num):

                    if lx2 == rx1+1:
                        _lx1 = random.choice([_ for _ in range(rx1+1)])
                        _lx2 = random.choice([_ for _ in range(lx2, r)])
                        blk_pairs.add(((_lx1, ly1, rx1, ry1), (lx2, ly2, _lx2, ry2), (typ1, typ2)))
                    elif lx1 == rx2+1:
                        _lx1 = random.choice([_ for _ in range(lx1, r)])
                        _lx2 = random.choice([_ for _ in range(rx2+1)])
                        blk_pairs.add(((lx1, ly1, _lx1, ry1), (_lx2, ly2, rx2, ry2), (typ1, typ2)))
            else:
                #print("col adjacent")
                #for ii in range(min(max(ry1-ly1+1, ry2-ly2+1), 5)):
                for ii in range(num):

                    if ly2 == ry1+1:
                        _ly1 = random.choice([_ for _ in range(ry1+1)])
                        _ly2 = random.choice([_ for _ in range(ly2, c)])
                        blk_pairs.add(((lx1, _ly1, rx1, ry1), (lx2, ly2, rx2, _ly2), (typ1, typ2)))
                    elif ly1 == ry2+1:
                        _ly1 = random.choice([_ for _ in range(ly1, c)])
                        _ly2 = random.choice([_ for _ in range(ry2+1)])
                        blk_pairs.add(((lx1, ly1, rx1, _ly1), (lx2, _ly2, rx2, ry2), (typ1, typ2)))

    return list(blk_pairs)

def sample_diff_pairs(sheet, blks, k=5):
    blk_pairs = set()
    random.seed(0)
    r, c = sheet.values.shape
    pmf = BlockTypePMF(
            {FunctionBlockType.inverse_dict["data"]: 1.0}
        )


    for _i, b1 in enumerate(blks):
        typ1 = b1.block_type.get_best_type().str()
        for _j, b2 in enumerate(blks):
            if _j <= _i:
                continue

            typ2 = b2.block_type.get_best_type().str()

            v, (lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2) = shrink(b1, b2)

            if not v:
                continue

            if row_adjacent((lx1, ly1, rx1, ry1), (lx2, ly2, rx2, ry2)):
                for ii in range(k):

                    if lx2 == rx1+1:
                        _lx1 = random.choice([_ for _ in range(lx1, rx1+1)])
                        _rx2 = random.choice([_ for _ in range(lx2, rx2+1)])
                        if b1.left_col < ly1:
                            _ly1 = random.choice([_ for _ in range(b1.left_col, ry1+1)])
                            _ry2 = random.choice([_ for _ in range(max(b2.left_col, _ly1), ry2+1)])
                            blk_pairs.add(((_lx1, _ly1, rx1, ry1), (lx2, ly2, _rx2, _ry2)))
                        else:
                            _ly2 = random.choice([_ for _ in range(b2.left_col, ry2+1)])
                            _ry1 = random.choice([_ for _ in range(max(b1.left_col, _ly2), ry1+1)])
                            blk_pairs.add(((_lx1, ly1, rx1, _ry1), (lx2, _ly2, _rx2, ry2)))
                    elif lx1 == rx2+1:
                        _rx1 = random.choice([_ for _ in range(lx1, rx1+1)])
                        _lx2 = random.choice([_ for _ in range(lx2, rx2+1)])
                        if b1.left_col < ly1:
                            _ly1 = random.choice([_ for _ in range(b1.left_col, ry1+1)])
                            _ry2 = random.choice([_ for _ in range(max(b2.left_col, _ly1), ry2+1)])
                            blk_pairs.add(((lx1, _ly1, _rx1, ry1), (_lx2, ly2, rx2, _ry2)))
                        else:
                            _ly2 = random.choice([_ for _ in range(b2.left_col, ry2+1)])
                            _ry1 = random.choice([_ for _ in range(max(b1.left_col, _ly2), ry1+1)])
                            blk_pairs.add(((lx1, ly1, _rx1, _ry1), (_lx2, _ly2, rx2, ry2)))
            else:
                for ii in range(k):
                    if ly2 == ry1+1:
                        _ly1 = random.choice([_ for _ in range(ly1, ry1+1)])
                        _ry2 = random.choice([_ for _ in range(ly2, ry2+1)])
                        if b1.top_row < lx1:
                            _lx1 = random.choice([_ for _ in range(b1.top_row, rx1+1)])
                            _rx2 = random.choice([_ for _ in range(max(b2.top_row, _lx1), rx2+1)])
                            blk_pairs.add(((_lx1, _ly1, rx1, ry1), (lx2, ly2, _rx2, _ry2)))
                        else:
                            _lx2 = random.choice([_ for _ in range(b2.top_row, rx2+1)])
                            _rx1 = random.choice([_ for _ in range(max(b1.top_row, _lx2), rx1+1)])
                            blk_pairs.add(((lx1, _ly1, _rx1, ry1), (_lx2, ly2, rx2, _ry2)))
                    elif ly1 == ry2+1:
                        _ry1 = random.choice([_ for _ in range(ly1, ry1+1)])
                        _ly2 = random.choice([_ for _ in range(ly2, ry2+1)])
                        if b1.top_row < lx1:
                            _lx1 = random.choice([_ for _ in range(b1.top_row, rx1+1)])
                            _rx2 = random.choice([_ for _ in range(max(b2.top_row, _lx1), rx2+1)])
                            blk_pairs.add(((_lx1, ly1, rx1, _ry1), (lx2, _ly2, _rx2, ry2)))
                        else:
                            _lx2 = random.choice([_ for _ in range(b2.top_row, rx2+1)])
                            _rx1 = random.choice([_ for _ in range(max(b1.top_row, _lx2), rx1+1)])
                            blk_pairs.add(((lx1, ly1, _rx1, _ry1), (_lx2, _ly2, rx2, ry2)))
    return list(blk_pairs)
