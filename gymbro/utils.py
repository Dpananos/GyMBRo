import sqlite3
import numpy as np
import pandas as pd
import sqlalchemy

from .connect import SqlConnection
from .clean import add_timezone_to_timestamp, convert_datetime_to_utc


def load_past_tweets_to_postgres():
    """Load past tweets to postgres."""


    with sqlite3.connect('database/Western_Tweet_Data.sqlite3') as conn:
        df = pd.read_sql_query("SELECT * FROM PreCovidWr order by created_at", conn)
        # Convert timestamp to utc
        df['created_at_utc'] = df.created_at.apply(lambda x:convert_datetime_to_utc(add_timezone_to_timestamp(x)))
        df['id'] = np.arange(len(df))
        df['wr'] = df.WR
        write_to_postgres = df[['id','created_at_utc','wr']]

        engine = SqlConnection.from_env().connect_sqlalchemy()
        write_to_postgres.to_sql('fact_pre_covid_wr', engine, if_exists='replace', index=False)
        return write_to_postgres


