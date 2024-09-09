from type.cell.cell_type import CellType


class FunctionCellType:

    METADATA = CellType("metadata", 0)
    DATA = CellType("data", 1)
    HEADER = CellType("header", 2)
    EMPTY = CellType("empty", 3)
    ATTRIBUTE = CellType("attributes", 4)
    #DERIVED = CellType("derived", 5)
    #NOTE = CellType("notes", 6)

    inverse_dict = {
        "metadata": METADATA,
        "data": DATA,
        "attributes": ATTRIBUTE,
        "header": HEADER,
        "empty": EMPTY,
        #"derived": DERIVED,
        #"notes": NOTE
    }

    id2str = {_.id(): _.str() for _ in inverse_dict.values()}

    @staticmethod
    def cell_type_count():
        return len(FunctionCellType.inverse_dict)
