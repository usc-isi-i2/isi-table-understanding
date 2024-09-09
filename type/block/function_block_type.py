from type.block.block_type import BlockType

class FunctionBlockType:
    METADATA = BlockType("metadata", 0)
    DATA = BlockType("data", 1)
    HEADER = BlockType("header", 2)
    ATTRIBUTE = BlockType("attributes", 3)

    inverse_dict = {
        "metadata": METADATA,
        "data": DATA,
        "header": HEADER,
        "attributes": ATTRIBUTE,
    }

    id2str = {_.id(): _.str() for _ in inverse_dict.values()}

    id2obj = {_.id(): _ for _ in inverse_dict.values()}

    @staticmethod
    def block_type_count():
        return len(FunctionBlockType.inverse_dict)
