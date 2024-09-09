class EdgeType:
    def __init__(self, edge_type: str, edge_id: int):
        self.edge_type = edge_type
        self.edge_id = edge_id

    def str(self):
        return self.edge_type

    def id(self):
        return self.edge_id

