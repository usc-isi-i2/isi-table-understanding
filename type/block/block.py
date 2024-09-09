import abc


class Block(abc.ABC):
    @abc.abstractmethod
    def get_block_type(self):
        pass

    @abc.abstractmethod
    def get_left_col(self):
        pass

    @abc.abstractmethod
    def get_right_col(self):
        pass

    @abc.abstractmethod
    def get_top_row(self):
        pass

    @abc.abstractmethod
    def get_bottom_row(self):
        pass
