from type.block.block_type import BlockType

class FunctionBlockTypeV2:
    METADATA = BlockType("metadata", 0)
    DATA = BlockType("data", 1)
    ATTRIBUTE = BlockType("attributes", 2)
    HEADER = BlockType("header", 3)
    EMPTY = BlockType("empty", 4)

    inverse_dict = {
        "metadata": METADATA,
        "data": DATA,
        "attributes": ATTRIBUTE,
        "header": HEADER,
        "empty": EMPTY
    }

    @staticmethod
    def block_type_count():
        return len(inverse_dict)
