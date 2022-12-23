import os
import psycopg2
import logging
from datetime import date
from dotenv import load_dotenv
from gymbro.scrape import Scraper, TwitterApiKeys, TwitterUser, fetch_latest_tweet_id

load_dotenv()

# Set up logging for scraping tweets
today = date.today().strftime("%Y-%m-%d")
log_file= f'logs/{today}.log'

logging.basicConfig(filename=log_file, 
                    encoding='utf-8', 
                    level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s:%(levelname)s:%(name)s:%(message)s')


user = TwitterUser(id=297549322, username='WesternWeightRm')
api_keys = TwitterApiKeys.from_env()
scraper = Scraper(user=user, api_keys=api_keys)


with psycopg2.connect(user='postgres', password='postgres', host='localhost', port=5432, database="gymbro") as con:

    cur = con.cursor()
    latest_tweet_id = fetch_latest_tweet_id(cur)
    tweets = scraper.get_tweets(max_results=100, since_id=latest_tweet_id)

    if tweets:
        for tweet in tweets:

            cur.execute("INSERT INTO tweets (id, created_at, author_id, text) VALUES (%s, %s, %s, %s)", (tweet.id, tweet.created_at, tweet.author_id, tweet.text))
            logging.info(f'Inserted tweet {tweet.id}')

        cur.close()
        con.commit()
    else:
        logging.info(f'No new tweets for {user.username}')
