from type.block.block import Block
from type.block.block_type_pmf import BlockTypePMF


class SimpleBlock(Block):
    def __init__(self, block_type: BlockTypePMF, left_col, right_col, top_row, bottom_row):
        self.block_type = block_type
        self.left_col = left_col
        self.right_col = right_col
        self.top_row = top_row
        self.bottom_row = bottom_row

        # Support for nested blocks
        self.children = []
        self.parent = None

    def __hash__(self):
        return hash(str(self))

    def get_block_type(self):
        return self.block_type

    def get_left_col(self):
        return self.left_col

    def get_right_col(self):
        return self.right_col

    def get_top_row(self):
        return self.top_row

    def get_bottom_row(self):
        return self.bottom_row

    def add_child(self, child_block):
        assert isinstance(child_block, self.__class__)
        assert child_block.parent is None

        self.children.append(child_block)
        child_block.parent = self

    # Note: Call either add_parent or add_child, not both for the same pair of blocks
    def add_parent(self, block):
        assert isinstance(block, self.__class__)
        block.add_child(self)

    def is_above(self, otherBlock):
        assert isinstance(otherBlock, self.__class__)

        if self.get_bottom_row() < otherBlock.get_top_row():
            return True

    def is_below(self, otherBlock):
        assert isinstance(otherBlock, self.__class__)

        if otherBlock.get_bottom_row() < self.get_top_row():
            return True

    def is_inside(self, otherBlock):
        assert isinstance(otherBlock, self.__class__)

        if otherBlock.get_right_col() != max(self.get_right_col(), otherBlock.get_right_col()):
            return False

        if otherBlock.get_left_col() != min(self.get_left_col(), otherBlock.get_left_col()):
            return False

        if otherBlock.get_top_row() != min(self.get_top_row(), otherBlock.get_top_row()):
            return False

        if otherBlock.get_bottom_row() != max(self.get_bottom_row(), otherBlock.get_bottom_row()):
            return False

        return True

    def is_adjacent(self, otherBlock):
        assert isinstance(otherBlock, self.__class__)

        # left, right
        if self.get_right_col() + 1 == otherBlock.get_left_col():
            if max(self.get_top_row(), otherBlock.get_top_row()) <= min(self.get_bottom_row(), otherBlock.get_bottom_row()):
                return True

        # right, left
        if self.get_left_col() - 1 == otherBlock.get_right_col():
            if max(self.get_top_row(), otherBlock.get_top_row()) <= min(self.get_bottom_row(), otherBlock.get_bottom_row()):
                return True

        # up, down
        if self.get_bottom_row() + 1 == otherBlock.get_top_row():
            if max(self.get_left_col(), otherBlock.get_left_col()) <= min(self.get_right_col(), otherBlock.get_right_col()):
                return True

        # down, up
        if self.get_top_row() - 1 == otherBlock.get_bottom_row():
            if max(self.get_left_col(), otherBlock.get_left_col()) <= min(self.get_right_col(), otherBlock.get_right_col()):
                return True

        return False

    def are_blocks_within_x_row_or_column(self, max_dist, otherBlock):
        assert isinstance(otherBlock, self.__class__)

        # left, right
        if otherBlock.get_left_col() >= self.get_right_col() + 1 and otherBlock.get_left_col() <= self.get_right_col() + max_dist:
            return True

        # right, left
        if otherBlock.get_right_col() >= self.get_left_col() - max_dist and otherBlock.get_right_col() <= self.get_left_col() - 1:
            return True

        # up, down
        if otherBlock.get_top_row() >= self.get_bottom_row() + 1 and otherBlock.get_top_row() <= self.get_bottom_row() + max_dist:
            return True

        # down, up
        if otherBlock.get_bottom_row() >= self.get_top_row() - max_dist and otherBlock.get_bottom_row() <= self.get_top_row() - 1:
            return True

        return False

    def are_blocks_horizontal(self, otherBlock):
        assert isinstance(otherBlock, self.__class__)

        if otherBlock.get_top_row() != self.get_top_row():
            return False
        if otherBlock.get_bottom_row() != self.get_bottom_row():
            return False

        return True

    def are_blocks_vertical(self, otherBlock):
        assert isinstance(otherBlock, self.__class__)

        if otherBlock.get_left_col() != self.get_left_col():
            return False
        if otherBlock.get_right_col() != self.get_right_col():
            return False

        return True

    def get_intersecting_area(self, otherBlock):
        assert isinstance(otherBlock, self.__class__)
        x_overlap = max(0,
                        min(otherBlock.get_right_col(), self.get_right_col()) -
                        max(otherBlock.get_left_col(), self.get_left_col()) + 1
                        )

        y_overlap = max(0,
                        min(otherBlock.get_bottom_row(), self.get_bottom_row()) -
                        max(otherBlock.get_top_row(), self.get_top_row()) + 1
                        )

        return x_overlap * y_overlap

    def get_area(self):
        return (self.get_right_col() - self.get_left_col() + 1) * (self.get_bottom_row() - self.get_top_row() + 1)

    def get_height(self):
        return self.get_bottom_row() - self.get_top_row() + 1

    def get_width(self):
        return self.get_right_col() - self.get_left_col() + 1

    def __eq__(self, other):  # For testing
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __str__(self):
        block_type = self.block_type.get_best_type().str() if self.block_type else None

        return "[ {} : ({},{}) to ({},{}) ]".format(block_type, self.top_row, self.left_col, self.bottom_row, self.right_col)
