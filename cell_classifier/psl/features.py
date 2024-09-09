import os
import numpy as np
from utils.date_parser import DateParser
from type.cell.semantic_cell_type import SemanticCellType
from cell_classifier.psl.feature_utils import *
import spacy
import usaddress

class Cell2Feat:
    def __init__(self):
        self.tags = [self.is_date, self.is_year,
                    self.is_number, self.is_empty, self.is_alpha,
                    self.is_upper, self.one_word, self.more_words,
                    self.has_special, self.first_alpha, self.has_num, self.has_alpha,
                    self.contain_loc, self.contain_org, self.is_zip, self.is_int]

        self.tagname = ["is_date", "is_year", "is_number",
                        "is_empty", "is_alpha", "is_upper", "one_word",
                        "more_words", "has_special", "first_alpha", "has_num", "has_alpha",
                        "contain_loc", "contain_org", "is_zip", "is_int"]

        self.tagname = [_.replace("_", "") for _ in self.tagname]

        self.tagvars = [3 for _ in range(len(self.tagname))]

        self.pred_name = "celltype"

    def serialize_feats(self, sheets, path, idx=0):
        if isinstance(sheets, list):
            str_list = [[] for _ in self.tags]

            for i, sheet in enumerate(sheets):

                temp_lists = self.serialize_feats(sheet, path, i)

                for j, tl in enumerate(temp_lists):

                    str_list[j].append(tl)

            return ["\n".join(tl) for tl in str_list]

        values = sheets.values

        str_list = []

        for tag in self.tags:

            str_list.append("\n".join(["{}\t{}\t{}\t{}".format(idx, x, y, int(tag(values[x][y])))
                                      for x in range(len(values))
                                      for y in range(len(values[x]))
                                      ]))
        return str_list

    def serialize_ce_lab(self, sheets, tags, idx=0):

        if isinstance(sheets, list):
            temp = []

            for i, sheet in enumerate(sheets):

                temp.append(self.serialize_ce_lab(sheet, tags[i], i))

            return "\n".join(temp)

        r, c = sheets.values.shape
        temp = []

        for j in range(r):
            for k in range(c):
                temp.append("{}\t{}\t{}\t{}\t{}".format(idx, j, k, tags[j][k], 1.0))

        return "\n".join(temp)

    def vec(self, sheets, tags, path):

        str_list = self.serialize_feats(sheets, path)

        if tags is not None:
            ce_str = self.serialize_ce_lab(sheets, tags)

            with open(os.path.join(path, "c2vlab_obs.txt"), "w+") as f:

                f.write(ce_str)

        for i, tagname in enumerate(self.tagname):

            with open(os.path.join(path, tagname + "_obs.txt"), "w+") as f:

                f.write(str_list[i])
        neighbor_str = self.neighbor(sheets)

        with open(os.path.join(path, "neighbor_obs.txt"), "w+") as f:
            f.write(neighbor_str)


    def write_predicates(self, pred_path):
        str_list = []

        for i in range(len(self.tagname)):
            str_list.append("{}\t{}\t{}".format(self.tagname[i], self.tagvars[i], "closed"))

        str_list.append("{}\t{}\t{}".format("c2vlab", 4, "closed"))

        str_list.append("{}\t{}\t{}".format("neighbor", 2, "closed"))

        str_list.append("{}\t{}\t{}".format(self.pred_name, 4, "open"))

        if pred_path is None:
            return

        with open(pred_path, "w+") as f:

            f.write("\n".join(str_list))

    def write_feats(self, sheets, annotated, tags, pred_path=None, path=None):

        self.vec(sheets, tags, path)

        self.write_objective(sheets, annotated, path)

        self.write_predicates(pred_path)

    def serialize_targets(self, sheets, path, i=0):

        if isinstance(sheets, list):

            return "\n".join([self.serialize_targets(sheet, path, i)
                              for i, sheet in enumerate(sheets)])

        (max_x, max_y) = sheets.values.shape

        return "\n".join(["{}\t{}\t{}\t{}".format(i, x, y, typ) for x in range(max_x)
                for y in range(max_y) for typ in SemanticCellType.inverse_dict.keys()])

    def serialize_truth(self, annotated, path, i=0):
        if isinstance(annotated, list):

            return "\n".join([self.serialize_truth(annotate, path, i)
                              for i, annotate in enumerate(annotated)])

        (max_x, max_y) = annotated.shape

        temp = []
        for x in range(max_x):
            for y in range(max_y):

                types = {_.str(): v for _, v in annotated[x][y].get_types().items()}

                for typ in SemanticCellType.inverse_dict.keys():
                    if typ not in types:
                        temp.append("{}\t{}\t{}\t{}\t{}".format(i, x, y, typ, 0.0))
                    else:
                        temp.append("{}\t{}\t{}\t{}\t{}".format(i, x, y, typ, types[typ]))

        return "\n".join(temp)

    def write_objective(self, sheets, annotated, path):

        if path is None:
            return

        target_str = self.serialize_targets(sheets, path)

        with open(os.path.join(path, self.pred_name + "_targets.txt"), "w+") as f:
            f.write(target_str)

        if annotated is not None:

            truth_str = self.serialize_truth(annotated, path)

            with open(os.path.join(path, self.pred_name + "_truth.txt"), "w+") as f:
                f.write(truth_str)

    def neighbor(self, sheets):
        temp = set()
        for sheet in sheets:
            r, c = sheet.values.shape
            for i in range(1, max(r, c)):
                temp.add((i-1, i))
        return "\n".join(["{}\t{}\t1.0".format(t[0], t[1]) for t in temp])

    def is_zip(self, value):
        if "-" in value:
            value = str(value).split("-")
            if len(value) != 2:
                return 0
            try:
                value[0] = str(int(value[0]))
                value[1] = str(int(value[1]))
                if len(value[0]) == 5 and len(value[1]) == 4:
                    return 1
                else:
                    return 0
            except:
                return 0
        else:
            try:
                value = int(value)
                if len(str(value)) == 5:
                    return 1
                else:
                    return 0
            except:
                return 0

    def contain_loc(self, value):
        if not self.is_string_literal(value):
            return 0
        ret = usaddress.parse(value)
        keys = set([tup[1] for tup in ret])
        if "PlaceName" in keys and "StateName" in keys:
            return 1
        if (len(value) == 2) and value.isupper():
            return 1
        return 0

    def contain_org(self, value):
        if not self.is_string_literal(value):
            return 0
        if len(value.split()) <= 1:
            return 0
        value = set(value.lower().split())
        if "institute" in value:
            return 1
        if "university" in value:
            return 1
        if "corporation" in value:
            return 1
        if "inc." in value:
            return 1
        if "department" in value:
            return 1
        return 0

    def date_range(self, value):
        if not self.is_string_literal(value):
            return 0

        temp = value.split("-")

        if len(temp) != 2:
            return 0

        if all([self.is_year(t) or self.is_partial_year(t) or
                self.is_quarter_or_yearmonth(t) or self.is_ymd_date(t) for t in temp]):
            return 1
        return 0

    def is_upper(self, value):
        return self.is_string_literal(value) and value.isupper()

    def word_cnt(self, value):
        return 0 if not self.is_string_literal(value) else len(value.strip().split())

    def less_words(self, value):
        cnt = self.word_cnt(value)
        return 1 if cnt > 1 and cnt <= 3 else 0

    def one_word(self, value):
        return 1 if self.word_cnt(value) == 1 else 0

    def more_words(self, value):
        return 1 if self.word_cnt(value) > 3 else 0

    def has_alpha(self, value):
        return 1 if self.is_string_literal(value) and alpha_regex.search(value) else 0

    def first_alpha(self, value):
        return 1 if self.is_string_literal(value) and len(value) > 0 and value[0].isalpha() else 0

    def has_num(self, value):
        return 1 if self.is_string_literal(value) and re.search('\d', value) else 0

    def is_year(self, value):
        try:
            int(float(value))
        except:
            return 0
        value = int(float(value))
        return 1 if DateParser(value).is_year() else 0

    def is_partial_year(self, value):
        try:
            return DataParser(int(value)).is_year()
        except:
            return DateParser(value).is_partial_year()

    def is_quarter_or_yearmonth(self, value):
        return DateParser(value).is_quarter_or_yearmonth()

    def is_ymd_date(self, value):
        return DateParser(value).is_ymd_date()

    def is_string_month(self, value):
        try:
            return DateParser(int(value)).is_string_month()
        except:
            return DateParser(value).is_string_month()

    def is_date(self, value):
        #if DateParser(value).is_date() or self.is_ymd_date(value) or \
        if self.is_ymd_date(value) or \
                self.is_string_month(value) or self.date_range(value):
            return 1
        return 0

    def has_special(self, value):
        if self.is_string_literal(value) and special_regex.search(value):
            return 1
        return 0

    def is_string_literal(self, value):
        if isinstance(value, str):
            return True
        return False

    def is_alpha(self, value):
        # Note the use of search instead of match
        # Match fails to match "1 kg"
        if self.is_string_literal(value) and alpha_regex.search(value):
            return 1
        return 0

    def is_number(self, value):
        if self.is_int(value) or self.is_float(value):
            return 1
        return 0

    def is_int(self, value):
        if isinstance(value, int):
            return 1
        try:
            int(value)
            return 1
            """
            if float(value) == int(float(value)):
                return 1
            else:
                return 0
            """
        except:
            return 0

        return 0

    def is_float(self, value):
        if isinstance(value, float):
            return 1
        try:
            float(value)
            return 1
        except:
            return 0
        return 0

    def is_empty(self, value):
        if value in empty_cell:
            return 1
        return 0
