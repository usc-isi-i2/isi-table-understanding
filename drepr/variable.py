class Slice:
    def __init__(self):
        pass


class IndexSlice(Slice):
    def __init__(self):
        super().__init__()
        self.type = "index_slice"
        self.idx = None


class RangeSlice(Slice):
    def __init__(self):
        super().__init__()
        self.type = "range_slice"
        self.start = None
        self.end = None
        self.step = None


class Location:
    def __init__(self):
        self.resource_id = None
        self.slices = []


class Variable:
    def __init__(self):
        self.id = "default_id"
        self.value = "literal"
        self.sorted = "null"
        self.type = "unspecified"
        self.unique = False

        self.missing_values = []

        self.location = None
