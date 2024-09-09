import abc


class AbstractFileReader(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_sheets(self):
        pass

    @abc.abstractmethod
    def get_sheet_by_index(self, idx):
        pass
