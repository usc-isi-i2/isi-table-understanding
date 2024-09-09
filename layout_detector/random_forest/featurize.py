import numpy as np

def block_relation_feats(blk1, blk2):
    feats = []
    feats.append(1 if blk1.is_above(blk2) else 0)
    feats.append(1 if blk1.is_below(blk2) else 0
)
    feats.append(1 if blk1.is_inside(blk2) else 0)
    feats.append(1 if blk1.is_adjacent(blk2) else 0)
    feats.append(1 if blk1.are_blocks_horizontal(blk2) else 0)
    feats.append(1 if blk1.are_blocks_vertical(blk2) else 0)
    feats.append(1 if blk1.get_intersecting_area(blk2) > 0 else 0)
    feats.append(1 if blk1.block_type.get_best_type().id() == blk2.block_type.get_best_type().id() else 0)
    feats.append(1 if blk1.block_type.get_best_type().id() != blk2.block_type.get_best_type().id() else 0)
    feats.append(blk1.block_type.get_best_type().id())
    feats.append(blk2.block_type.get_best_type().id())
    return feats

def get_block_labels(layout):
    pairs, labels = [], []
    for j in range(len(layout.outEdges)):
        v1 = j
        for _type, v2 in layout.outEdges[v1]:
            pairs.append((j, v1))
            labels.append(_type.id())
    return pairs, labels
