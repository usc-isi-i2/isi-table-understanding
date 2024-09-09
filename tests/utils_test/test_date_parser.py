from util.date_parser import DateParser
from datetime import datetime
import unittest


class TestDateParser(unittest.TestCase):

    def test_date_parser(self):

        assert DateParser("Jan").is_string_month() == True
        assert DateParser(u"Jan").is_string_month() == True
        assert DateParser(u"Janu").is_string_month() == False
        assert DateParser(u"January").is_string_month() == True
        assert DateParser(r"January").is_string_month() == True

        assert DateParser(1).is_date() == True
        assert DateParser(32).is_date() == False

        assert DateParser("2001M1").is_quarter_or_yearmonth() == True
        assert DateParser("2001Q02").is_quarter_or_yearmonth() == True
        assert DateParser("201212").is_quarter_or_yearmonth() == False

        assert DateParser(2012).is_year() == True
        assert DateParser('2012').is_year() == True
        assert DateParser(2201).is_year() == False
        assert DateParser(1899).is_year() == False

        assert DateParser('January').is_ymd_date() == False
        assert DateParser('2001').is_ymd_date() == False
        assert DateParser('2001/01').is_ymd_date() == True
        assert DateParser('1/1/18').is_ymd_date() == True

        assert DateParser('1992.22').is_ymd_date() == True
        assert DateParser('199.22').is_ymd_date() == False
        assert DateParser('123.456').is_ymd_date() == False
        assert DateParser('2001.232').is_ymd_date() == False

        assert DateParser('BIO_2004').is_partial_year() == True
        assert DateParser('2001:').is_partial_year() == True
        assert DateParser('Title').is_partial_year() == False
        assert DateParser('This happened in year 2001').is_partial_year() == True
        assert DateParser('1 to 2001').is_partial_year() == False
        assert DateParser('1').is_partial_year() == False
        assert DateParser('2001').is_partial_year() == True
        assert DateParser(2015).is_partial_year() == True
        assert DateParser(datetime(2016, 1, 1)).is_partial_year() == True
