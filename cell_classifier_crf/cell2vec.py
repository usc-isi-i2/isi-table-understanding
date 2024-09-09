from cell_classifier_crf.feature_utils import word_regex, alpha_regex, alphanum_regex, symbol_regex, empty_cell

import numpy as np
from util.date_parser import DateParser

class cell2vec:
    def __init__(self, value):
        self.value = value
        self.tags = [self.is_ymd_date, self.is_quarter_or_yearmonth, self.is_string_month, self.is_date,
                    self.is_year, self.is_partial_year,
                    self.is_int,
                    self.is_number, self.is_empty, self.is_alpha]#,
                    #self.is_string_literal, self.is_string, self.is_float, self.is_error] #Extra stuff
                    # self.is_upper, self.is_lower, self.is_title

    def vec(self):
        return np.array(list(map(lambda x: x(self.value), self.tags)))

    def is_upper(self, value):
        return self.is_string_literal(value) and value.isupper()

    def is_lower(self, value):
        return self.is_string_literal(value) and value.islower()

    def is_title(self, value):
        return self.is_string_literal(value) and value.istitle()

    def is_year(self, value):
        return DateParser(value).is_year()

    def is_partial_year(self, value):
        return DateParser(value).is_partial_year()

    def is_quarter_or_yearmonth(self, value):
        return DateParser(value).is_quarter_or_yearmonth()

    def is_ymd_date(self, value):
        return DateParser(value).is_ymd_date()

    def is_string_month(self, value):
        return DateParser(value).is_string_month()

    # We are not adding a check of numeric month because it is covered under date (1..31)

    def is_date(self, value):
        return DateParser(value).is_date()

    def is_string_literal(self, value):
        if isinstance(value, str):
            return True
        return False

    def is_word(self, value):
        # TODO: Add dictionary to check
        if self.is_string_literal(value) and word_regex.match(value):
            return 1
        return 0

    def is_string(self, value):
        if value != '':
            return 1
        return 0

    def is_alpha(self, value):
        # Note the use of search instead of match
        # Match fails to match "1 kg"
        if self.is_string_literal(value) and alpha_regex.search(value):
            return 1
        return 0

    def is_alphanum(self, value):
        # str.isalnum()
        if self.is_string_literal(value) and alphanum_regex.match(value):
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

    def is_symbol(self, value):
        if self.is_string_literal(value) and symbol_regex.match(value):
            return 1
        return 0

    def is_empty(self, value):
        if value in empty_cell:
            return 1
        return 0

    def is_error(self, value):
        return 0

