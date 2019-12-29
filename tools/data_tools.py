import sqlite3
import pandas as pd

from .db_tools import get_weather


def fetch_training(db_loc="database/Western_Tweet_Data.sqlite3"):

    """
    Function to query training data from databases.
    Function takes as argument location of the sqlite database.
    The merge_asof is perfomed in pandas and is pretty fast provided
    there is like 40K observations.
    """

    with sqlite3.connect(db_loc) as con:

        # Query for weightroom data.
        # Two tables exist; HistoricWR and WesternWR
        # Historic has data from 2014-2017 approximately
        # Western WR has 2017 onwards
        # Join historic and recent data with a UNION in sqlite.
        # Select data up until yesterday because we are predicting weight room today

        query = """
            WITH WRDATA AS
            (SELECT created_at, WR
                FROM WESTERNWR
                UNION
                SELECT created_at, WR
                FROM HISTORICWR
                WHERE CREATED_AT<(SELECT MIN(CREATED_AT) FROM WESTERNWR)
              )
            SELECT *
            FROM WRDATA
            WHERE CREATED_AT< DATE('NOW','LOCALTIME')
            ORDER BY CREATED_AT
                """
        # Data needs to be ordered for the join to work.  Hence, do an ORDER BY

        wr = pd.read_sql(query, con, parse_dates=["created_at"])

        # Query weather database.
        # This doesn't use all the columns because there are a lot of nulls

        query = """
        SELECT
            created_at,
            apparentTemperature,
            humidity,
            precipIntensity,
            precipProbability,
            IFNULL(precipType ,'NoPrecip' ) as precipType,
            pressure,
            visibility,
            windBearing,
            windspeed
        FROM LondonWeather
        WHERE created_at < DATE('NOW','LOCALTIME')
            """

        # Weather data now in python
        weather = pd.read_sql(query, con, parse_dates=["created_at"])

    # Here is the merge.  Merge closest weather measurement on the assumption that weather does not change too rapidly.
    training = pd.merge_asof(wr, weather, on="created_at", tolerance=pd.Timedelta("2 hours"))
    X = training.drop("WR", axis=1)
    y = training.WR.values

    return X, y


def fetch_weather():

    """
    Function to fetch today's weather / weather forecast.

    Will be used to predict the number of people in the weight room on the day
    the script is run.
    """

    # This is lazy, but it works.
    # Basically, for consistency, I am going to fetch today's forecast
    # then, I write it to a sqlite database in memory
    # then, run the query I ran before.  Easy.
    today = pd.to_datetime("today")
    weather = get_weather(lat = 43.0356, lon = -81.1539, t=today)

    with sqlite3.connect("") as con:

        weather.to_sql("LondonWeather", con=con)

        query = """
                SELECT
                    created_at,
                    apparentTemperature,
                    humidity,
                    precipIntensity,
                    precipProbability,
                    IFNULL(precipType ,'NoPrecip' ) as precipType,
                    pressure,
                    visibility,
                    windBearing,
                    windspeed
                FROM LondonWeather
                    """

        wtoday = pd.read_sql(query, con, parse_dates=["created_at"])
        when_open = wtoday.created_at.dt.hour >= 6
        wtoday = wtoday[when_open]

        # Drop the table from memory
        con.execute("drop table if exists LondonWeather")

    return wtoday

def fetch_wr(db_loc="database/Western_Tweet_Data.sqlite3"):

    """
    Fetches how many people in are in the weight room today.
    Will be used in making a plot for tweeting.
    """

    with sqlite3.connect(db_loc) as con:
        query = """
                SELECT created_at, WR
                FROM WesternWR
                WHERE DATE(created_at, 'LOCALTIME') == DATE('NOW','LOCALTIME')
                ORDER BY created_at
                """
        wr = pd.read_sql(query, con, index_col=["created_at"], parse_dates=["created_at"])

    return wr
