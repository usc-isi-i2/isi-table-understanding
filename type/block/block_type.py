class BlockType:

    def __init__(self, block_type: str, block_id: int):
        self.block_type = block_type
        self.block_id = block_id

    def str(self):
        return self.block_type

    def id(self):
        return self.block_id
