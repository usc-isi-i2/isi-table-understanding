from type.cell.cell_type import CellType


class SemanticCellType:

    EMPTY = CellType("empty", 0)
    CARDINAL = CellType("cardinal", 1)
    STRING = CellType("string", 2)
    DATETIME = CellType("datetime", 3)
    LOCATION = CellType("location", 4)
    ORG = CellType("organization", 5)
    ORDINAL = CellType("ordinal", 6)
    NOMINAL = CellType("nominal", 7)
    PERSON = CellType("person", 8)
    #EVENT = CellType("event", 9)

    inverse_dict = {
        "ordinal": ORDINAL,
        "cardinal": CARDINAL,
        "nominal": NOMINAL,
        "location": LOCATION,
        "person": PERSON,
        "organization": ORG,
        #"event": EVENT,
        "datetime": DATETIME,
        "empty": EMPTY,
        "string": STRING
    }

    id2str = {_.id(): _.str() for _ in inverse_dict.values()}

    id2obj = {_.id(): _ for _ in inverse_dict.values()}

    @staticmethod
    def cell_type_count():
        return len(SemanticCellType.inverse_dict)
