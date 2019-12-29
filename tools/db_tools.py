import numpy as np
import datetime as dt
import forecastio
import pandas as pd
import pickle
import re
import sqlite3
import time
import tweepy

from .tools import wr


def load_keys():

    with open('weather_api_keys.txt','rb') as f:
        weather_api_keys = pickle.load(f)

    with open('twitter_api_keys.txt','rb') as f:
        twitter_api_keys = pickle.load(f)

    return twitter_api_keys, weather_api_keys


def extract_tweets(db_loc = 'database/Western_Tweet_Data.sqlite3'):

    '''
    Try getting oldest id from database and passing to tweepy functions.
    Should speed things up
    '''

    with sqlite3.connect(db_loc) as con:

        df = pd.read_sql('select * from WesternWR order by created_at desc limit 1', con = con)
        last_id = df.idstr.values[0]

    twitter_api_keys, _ = load_keys()
    _consumer_key = twitter_api_keys['consumer_key']
    _consumer_secret = twitter_api_keys['consumer_secret']
    _access_key = twitter_api_keys['access_key']
    _access_secret = twitter_api_keys['access_secret']

    auth = tweepy.OAuthHandler(_consumer_key, _consumer_secret)
    auth.set_access_token(_access_key, _access_secret)
    api = tweepy.API(auth)

    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name='WesternWeightRm',
                                   count=200,
                                   since_id=last_id,
                                  include_rts=False)

    #save most recent tweets
    alltweets.extend(new_tweets)
    alltweets = [j for j in alltweets if not hasattr(j,'retweeted_status')]
    outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8").decode('utf-8')] for tweet in alltweets]

    return outtweets


def get_weather(lat = 43.0356, lon = -81.1539, t=None):

    _, weather_api_keys = load_keys()
    forecast = forecastio.load_forecast(weather_api_keys['weather_api_key'], lat, lon, time =t)
    forcasted_weather = pd.DataFrame(forecast.json['hourly']['data'])
    forcasted_weather['created_at'] =( pd.to_datetime(forcasted_weather.time, unit='s').
                        dt.tz_localize('UTC').
                        dt.tz_convert('America/Toronto').
                        dt.tz_localize(None)
                        )
    return forcasted_weather


def update_weather_db(db_loc = 'database/Western_Tweet_Data.sqlite3'):

    _, weather_api_keys = load_keys()

    with sqlite3.connect(db_loc) as con:

        #First step is to determine what was the last day I extracted weather.
        query = 'Select MAX(date(created_at)) as date from LondonWeather'
        last_date = pd.read_sql(query, con, parse_dates=['date']).date.iloc[0]
        get_date = last_date + pd.Timedelta('1 day')
        yesterday  = pd.to_datetime('today') - pd.Timedelta('1 day') #Don't want today's weather

        date_range = pd.date_range(get_date, yesterday)

        concat_me = []
        for t in date_range:
            forcasted_weather=get_weather(lat=43.0356, lon=-81.1539, t=t)
            concat_me.append(forcasted_weather)

        if concat_me:
            update_with = pd.concat(concat_me)

            update_with.to_sql('LondonWeather', con=con, if_exists='append', index=False)

    return None


def update_tweet_db(db_loc = 'database/Western_Tweet_Data.sqlite3'):

    outtweets = extract_tweets()
    #extract_tweets() returns empty list if no new tweets
    if len(outtweets)>0:
        df = pd.DataFrame(outtweets, columns=['idstr','created_at','text'])
        df['created_at'] = df.created_at.dt.tz_localize('UTC').dt.tz_convert('America/Toronto').dt.tz_localize(None)
        df['WR'] = df.text.apply(wr)
        df['created_at'] = pd.to_datetime(df.created_at)
        df['created_at'] = df.created_at.astype(str)
        df = df[df.WR>0]
        df.drop('text', inplace = True, axis = 1)

        with sqlite3.connect(db_loc) as con:

            dbs = pd.read_sql('select * from WesternWR', con=con)
            new = df[~df.idstr.isin(dbs.idstr)]
            new.to_sql('WesternWR', if_exists='append', index=False, con=con)

    return None