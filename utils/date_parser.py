from utils.string_utils import string2int, is_string_literal, data_to_string
from dateutil.parser import parse
from datetime import date, datetime
import re

date_separators = r'/-. '


# TODO: End goal -> Parse sequence of dates, including resolving ambiguities in order of features, presence or absence of features
# TODO: Use dateparser library?

class DateParser:
    months = set(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov',
                  'dec', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                  'october', 'november', 'december'])

    def __init__(self, value):
        self.value = value
        self.string_value = data_to_string(value)
        self.int_value = string2int(value)

    # Test cases: 2001M1 - true, 2002Q02 - true, 2001212 - false
    def is_quarter_or_yearmonth(self):
        p1 = self.string_value[:4]
        p2 = self.string_value[4:5]
        p3 = self.string_value[5:]

        if DateParser(p1).is_year() and DateParser(p3).is_numeric_month() and not p2.isdigit():
            return True
        return False

    def is_year_range(self, value):
        if value != None and value >= 1900 and value <= 2200:
            return True
        return False

    def is_year(self):
        return self.is_year_range(self.int_value)

    def is_partial_date(self):
        if isinstance(self.value, str):
            return False
            # TODO: SPlit on symbols => check mapping to months
            # split on non-numbers => map to years
            # prefix = self.value[:4]
            # suffix = self.value[-4:]

            # if prefix.isdigit() and self.is_year_range(prefix):
            #     return True
            # elif suffix.isdigit() and self.is_year_range(suffix):
            #     return True

        return False

    def is_partial_year(self):
        match = re.search(r'\d+', self.string_value)
        if match is not None:
            return DateParser(match.group()).is_year()
        return False

    def is_string_month(self):
        if self.string_value.lower() in self.months:
            return True

        return False

    def is_numeric_month(self):
        if self.int_value != None and self.int_value <= 12 and self.int_value >= 1:
            return True  # Give low weightage to this?

        return False

    def is_date(self):
        if self.int_value != None and self.int_value >= 1 and self.int_value <= 31:
            return True  # Todo very low weights

        return False

    # TODO: Need better date parser
    # TODO: Nov-2016
    def is_ymd_date(self):
        if isinstance(self.value, date) or isinstance(self.value, datetime):
            return True
        # TODO: This parser can turn many inputs to dates. Too many false positives
        # THis is also parsing strings like january into dates!! ugh!!
        try:
            # A few sanity checks
            # Length of string must be at least 6 (eg. 1/1/18)
            # String must have at least 6 numeric characters (YYYY/MM / YY/MM/DD)
            # Some date formats will not recognized because of this. 12/12, etc.. But strict matching is necessary to avoid too many false positives
            if len(self.string_value) < 7:
                return False
            if sum(c.isdigit() for c in self.string_value) < 6:
                return False

            d = parse(self.string_value)
            if self.is_year_range(d.year):
                return True
        except:
            return False

        return False
