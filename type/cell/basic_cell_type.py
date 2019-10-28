from type.cell.cell_type import CellType


class BasicCellType:
    EMPTY = CellType("EMPTY", 0)
    DATA = CellType("_DATA_", 1)
    DATE = CellType("DATE", 2)
    META = CellType("META", 3)

    # Note: IDs are different in declaration and inverse dictionary.
    # To avoid confusion, i'm putting this in another file
    # inverse_dict = {
    #     0: EMPTY,
    #     1: META,
    #     2: DATE,
    #     3: DATA
    # }

    @staticmethod
    def cell_type_count():
        return 4
