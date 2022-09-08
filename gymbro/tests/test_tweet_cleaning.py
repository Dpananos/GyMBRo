from distutils.command.clean import clean
from unittest import case
import pytest 
from gymbro.tweet_cleaning import clean_text, extract_text


class TestCleaning:

    def test_cleaning_non_alphanumeric(self):

        case_1 = "WR - 1 CM - 1 SPIN - 1"
        assert clean_text(case_1) == 'WR 1 CM 1 SPIN 1'

        case_2 = "wr: 20 cm: 9 spin: 0"
        assert clean_text(case_2) == 'WR 20 CM 9 SPIN 0'

        case_3 = "WR- CM- Spin_"
        assert clean_text(case_3) == 'WR CM SPIN'

        case_4 = "WR 103 CM 10 SPIN 6 😉"
        assert clean_text(case_4) == 'WR 103 CM 10 SPIN 6'

        case_5 = "WR 10\nCM 20\n SPIN 30"
        assert clean_text(case_5) == "WR 10 CM 20 SPIN 30"


    def test_extract_text(self):

        case_1 = 'WR 10 CM 20 SPIN 30'
        assert extract_text(case_1, "WR") == "10"
        assert extract_text(case_1, "CM") == "20"
        assert extract_text(case_1, "SPIN") == "30"
        assert extract_text(case_1, "PO") == "NaN"

        case_2 = "WRACK WR 20 CM 20 SPIN 20"
        assert extract_text(case_2, "WR") == "20"

        case_3 = "WR1LD UP WR 20"
        assert extract_text(case_3, "WR") == "20"



