
class CellType:

    def __init__(self, cell_type: str, cell_id: int):
        self.cell_type = cell_type
        self.cell_id = cell_id

    def str(self):
        return self.cell_type

    def id(self):
        return self.cell_id

    def __hash__(self):
        return hash(self.cell_type)

    # # TODO: Remove this safely
    # @classmethod
    # def max_id(cls):
    #     # [EMPTY, DATA, DATE, META]
    #     # Need some method to return this automatically
    #     return 4

#
# # TODO: Remove this safely and use basic_cell_type
# # TODO: (minor) can we move these variables inside the celltype class?
# EMPTY = CellType("EMPTY", 0)
# DATA = CellType("_DATA_", 1)
# DATE = CellType("DATE", 2)
# META = CellType("META", 3)
