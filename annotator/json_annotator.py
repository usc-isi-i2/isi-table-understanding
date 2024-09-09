from annotator.abstract_annotator import AbstractAnnotator


class JSONAnnotator(AbstractAnnotator):
    def get_annotation(self, sheet_index, sheet, tags, blocks, layout) -> dict:
        return dict()
