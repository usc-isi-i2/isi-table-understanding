from type.block.block_type import BlockType

"""
If you need different block types, please create your own class. Do not change the block types in this class.
"""
class BasicBlockType:
    EMPTY = BlockType("empty_block", 0)
    VALUE = BlockType("value_block", 1)
    ATTRIBUTE = BlockType("attribute_block", 2)
    GLOBAL_ATTRIBUTE = BlockType("global_attribute_block", 3)
    HEADER = BlockType("header_block", 4)

    str_to_block_type = {
        "empty_block": EMPTY,
        "value_block": VALUE,
        "attribute_block": ATTRIBUTE,
        "global_attribute_block": GLOBAL_ATTRIBUTE,
        "header_block": HEADER
    }

    @staticmethod
    def block_type_count():
        return len(BasicBlockType.str_to_block_type)


"""
Define your own block types here or in other classes derived from BasicBlockType
"""
class AdvancedBlockType(BasicBlockType):
    pass