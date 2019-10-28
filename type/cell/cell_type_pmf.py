from type.cell.cell_type import CellType

class CellTypePMF:
    def __init__(self, classes: dict):
        self.classes = classes

    def get_types(self) -> dict:
        return self.classes

    def get_best_type(self) -> CellType:  # TODO: Should we return string or something else?
        best_class = ""
        best_prob = 0.0

        for k in self.classes:
            if self.classes[k] > best_prob:
                best_class = k
                best_prob = self.classes[k]

        return best_class

    def __eq__(self, other):  # For testing
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __repr__(self):
        return self.classes.__repr__()
