import os
from data_loader.binhs_layout_file_loader import BinhsLayoutFileLoader
from reader.file_reader import get_file_reader


class LoadSyntheticData:
    def __init__(self, data_path='/Users/work/Documents/table_generator/GENERATED_FILES/',
                 annotation_path='/Users/work/Documents/table_generator/GENERATED_ANNOTATIONS/'):
        self.data_path = data_path
        self.annotation_path = annotation_path

    def load_files(self):
        sheet_list = []
        cell_tags_list = []
        block_list = []
        layout_list = []

        for dirpath, dirnames, filenames in os.walk(self.annotation_path):
            for fn in filenames:
                # if len(sheet_list) >= 2:
                #     break

                if fn.endswith(".yaml") and not fn.startswith("~"):
                    uid = fn[:-5]
                    # Check if xlsx file of same name exists in data_path
                    xlsx_file = os.path.join(self.data_path, uid + ".xlsx")
                    print(xlsx_file)

                    try:
                        assert os.path.isfile(xlsx_file)
                    except:
                        print("Matching datafile not found")
                        continue

                    annotation_file = os.path.abspath(os.path.join(dirpath, fn))
                    try:
                        print("Loading annotation file: {}".format(annotation_file))
                        cell_tags, blocks, layouts = BinhsLayoutFileLoader(annotation_file).get_cell_tags_blocks_and_layout()

                        print("Loading excel file: {}".format(xlsx_file))
                        reader = get_file_reader(xlsx_file)
                        sheet = reader.get_sheet_by_index(0)

                        cell_tags_list.append(cell_tags)
                        block_list.append(blocks)
                        layout_list.append(layouts)
                        sheet_list.append(sheet)

                    except:
                        print("Failed to load file: ", fn)

        return sheet_list, cell_tags_list, block_list, layout_list


