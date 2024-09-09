import abc
from type.layout.layout_graph import LayoutGraph


class LayoutDetector(abc.ABC):
    @abc.abstractmethod
    def detect_layout(self, sheet, tags, blocks) -> LayoutGraph:
        pass
