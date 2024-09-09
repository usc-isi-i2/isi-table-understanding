import numpy as np
from type.cell.function_cell_type import FunctionCellType

def get_row_feats(sheet):
    r, c = sheet.values.shape
    feats = []

    for i in range(r):
        temp = np.array([sheet.meta['farr'][i][j] for j in range(c)])
        feats.append(np.max(temp, axis=0))

    return np.array(feats)

def get_row_labels(sheet, tags):
    r, c = sheet.values.shape
    labs = []
    pred = [[None for j in range(c)] for i in range(r)]

    for block in tags:
        lx, ly = block.top_row, block.left_col
        rx, ry = block.bottom_row, block.right_col
        lab = block.block_type.get_best_type()

        for i in range(lx, rx + 1):
            for j in range(ly, ry + 1):
                #print(i, j, r, c)
                pred[i][j] = lab

    for i in range(r):
        lab = {}
        for j in range(c):
            if pred[i][j] is None:
                continue
            idx = pred[i][j].str()
            if idx in ["metadata", "data", "header"]:
                if idx not in lab:
                    lab[idx] = 0
                lab[idx] += 1

        if len(lab) == 0:
            labs.append("empty")
        else:
            labs.append(sorted(lab.items(), key=lambda x: x[1], reverse=True)[0][0])

    return np.array([FunctionCellType.inverse_dict[_].id() for _ in labs])
