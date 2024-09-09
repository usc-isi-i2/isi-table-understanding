from type.block.block_type import BlockType
from type.block import block_type


"""
Probability distribution of different block types
"""
class BlockTypePMF:
    def __init__(self, classes: dict):
        self.classes = classes

    # TODO: Enforce dict key type
    def get_types(self) -> dict:
        return self.classes

    def get_best_type(self) -> BlockType:
        best_class = None
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

# Few predefined classes
# EMPTY_CLASS = BlockClass({block_type.EMPTY: 1})
# ATTRIBUTE_CLASS
