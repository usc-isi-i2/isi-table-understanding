import abc


class AbstractAnnotator(abc.ABC):
    @abc.abstractmethod
    def get_annotation(self, sheet_index, sheet, tags, blocks, layout) -> dict:
        pass
