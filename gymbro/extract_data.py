import sqlite3
import pandas as pd
from .tweet_cleaning import clean_text, extract_text

def extract_data(db_loc: str) -> pd.DataFrame:

    with sqlite3.connect(db_loc) as con:

        # Extract the pre-data first, which has the WR column already
        extract_pre_covid_query = '''
        select 
            datetime(created_at) as created_at,
            CAST(WR as REAL) as WR 
        from 
            PreCovidWR
        order by 1 desc
        '''

        pre_covid = pd.read_sql(extract_pre_covid_query, con)
        pre_covid['created_at'] = pd.to_datetime(pre_covid.created_at)

        # Extract the post-data second, because it needs cleaning.
        extract_post_covid_query = '''
        select
            datetime(created_at) as created_at,
            text
        from 
            PostCovidWR
        order by 1 desc
        '''

        post_covid = pd.read_sql(extract_post_covid_query, con)
        post_covid['WR'] = post_covid.text.apply(lambda x: extract_text(clean_text(x), 'WR')).astype(float)
        post_covid = post_covid.drop(columns = ['text'])
        post_covid['created_at'] = pd.to_datetime(post_covid.created_at)

        return pd.concat([post_covid, pre_covid])
