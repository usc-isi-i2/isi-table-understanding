import os
from data_loader.layout_file_loader import LayoutFileLoader


class LoadTrainingData:
    def __init__(self, data_path='data/layout_files/'):
        self.data_path = data_path

    def load_annotation_files(self):

        block_list = []
        layout_list = []

        for dirpath, dirnames, filenames in os.walk(self.data_path):
            for fn in filenames:
                if fn == "ann.json":
                    annotation_file = os.path.abspath(os.path.join(dirpath, fn))
                    try:
                        print("Loading annotation file: {}".format(annotation_file))
                        blocks_and_layouts = LayoutFileLoader(annotation_file).get_blocks_and_layout()
                        for b, l in blocks_and_layouts:
                            block_list.append(b)
                            layout_list.append(l)
                    except:
                        print("Failed to load file: ", fn)

        return block_list, layout_list