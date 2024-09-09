import numpy as np

def get_cell_feat(sheet,  x, y):
    features = [sheet.meta['farr'][x][y]]
    for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        try:
            features.append(sheet.meta['farr'][x+dx][y+dy])
        except:
            features.append([0 for _ in sheet.meta['farr'][x][y]])

    return np.array(features).flatten()

def get_row_feats(sheet):
    r, c = sheet.values.shape
    feats = []

    for i in range(r):
        temp = np.array([sheet.meta['farr'][i][j] for j in range(c)])
        feats.append(np.maximum(temp))

    return np.array(feats)

def get_row_labels(sheet, tags):
    r, c = sheet.values.shape
    labs = []
    for i in range(r):
        lab = None
        for j in range(c):
            if tags[i][j].get_best_type().str() in ["metadata", "data", "header"]:
                lab = tags[i][j].get_best_type().id()
        labs.append(lab)
    return labs

def get_feat_tuple(sheet):
    node_feat, edge, edge_feat = [], [], []
    node_index = {}
    r, c = sheet.values.shape
    for i in range(r):
        for j in range(c):
            node_index[(i, j)] = len(node_feat)
            node_feat.append(sheet.meta['farr'][i][j])
    for i in range(r):
        for j in range(c):
            idx = node_index[(i, j)]
            for (i2, j2) in [(i, j+1), (i+1, j)]:
                if i2 < r and j2 < c:
                    idx2 = node_index[(i2, j2)]
                    edge.append((idx, idx2))
                    edge_feat.append(node_feat[idx] + node_feat[idx2])
    return (np.array(node_feat), np.array(edge), np.array(edge_feat))

def get_features(sheets):
    #return [[get_cell_feat(sheet, x, y) for x, row in enumerate(sheet.values)
    #        for y, _ in enumerate(row)] for sheet in sheets]
    return np.array([get_feat_tuple(sheet) for sheet in sheets])
