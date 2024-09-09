from type.layout.edge_type import EdgeType
"""
If you need different edge types, please create your own class. Do not change the edge types in this class.
"""
class BasicEdgeType:
    #NULL = EdgeType("null", 0)
    NULL = EdgeType("empty", 0)
    # FROM BLOCK -> TO BLOCK
    # HEADER_BLOCK -> ATTRIBUTE_BLOCK
    # HEADER_BLOCK -> GLOBAL_ATTRIBUTE_BLOCK
    HEADER = EdgeType("header", 1)
    # FROM BLOCK -> TO BLOCK
    # ATTRIBUTE_BLOCK -> VALUE_BLOCK
    ATTRIBUTE = EdgeType("attribute", 2)
    # FROM BLOCK -> TO BLOCK
    # GLOBAL_ATTRIBUTE_BLOCK -> VALUE_BLOCK
    GLOBAL_ATTRIBUTE = EdgeType("global_attribute", 3)
    # FROM BLOCK -> TO BLOCK
    # ATTRIBUTE_BLOCK -> ATTRIBUTE_BLOCK
    SUPERCATEGORY = EdgeType("supercategory", 4)

    str_to_edge_type = {
        #"null": NULL,
        "empty": NULL,
        "header": HEADER,
        "attribute": ATTRIBUTE,
        "global_attribute": GLOBAL_ATTRIBUTE,
        "supercategory": SUPERCATEGORY
    }

    inv_edge_labels = {
        0: NULL,
        1: HEADER,
        2: ATTRIBUTE,
        3: GLOBAL_ATTRIBUTE,
        4: SUPERCATEGORY
    }

    label_keys = [
        0, 1, 2, 3, 4
    ]

    @staticmethod
    def block_type_count():
        return len(BasicEdgeType.str_to_edge_type)

