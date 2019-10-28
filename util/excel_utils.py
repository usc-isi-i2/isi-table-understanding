import re


def col2num(col):
    num = 0
    for c in col:
        num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num - 1


def num2col(idx):
    if idx <= 25:
        return chr(ord('A') + idx)
    return num2col(idx//26 - 1) + chr(ord('A') + idx%26)


def cell2num(cell_name):
    row = int(re.search("[0-9]+", cell_name).group(0))
    col = col2num(re.search("[a-z]+", cell_name, flags=re.IGNORECASE).group(0))

    return row - 1, col


def excel_range2bbox(r):
    bb = r.split(":")
    if len(bb) == 1:
        row, col = cell2num(bb[0])
        return (row, col, row, col)
    else:
        top_row, left_col = cell2num(bb[0])
        bottom_row, right_col = cell2num(bb[1])
        return (top_row, left_col, bottom_row, right_col)
