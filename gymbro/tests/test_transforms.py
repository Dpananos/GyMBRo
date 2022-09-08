from sqlite3 import DatabaseError
import pytest
import pandas as pd
from gymbro.transforms import TimeFeatureExtractor

class TestTransforms():


    def test_time_feature_extractor(self):

        t1 = pd.Series(pd.to_datetime('2022-12-30 00:02:01'))

        tfe = TimeFeatureExtractor()

        transformed = tfe.fit_transform(t1)

        assert type(transformed) == pd.DataFrame

        expected_columns =  ['year',
                             'month',
                             'week',
                             'day',
                             'month_progress',
                             'year_progress',
                             'time']

        assert transformed.columns.tolist() == expected_columns

        assert transformed.time.values == 0 + 2.0/60

        assert transformed.day.values == 4

