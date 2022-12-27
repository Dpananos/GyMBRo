import logging
from datetime import date
from dotenv import load_dotenv
from gymbro.scrape import Scraper, TwitterApiKeys, TwitterUser
from gymbro.connect import SqlConnection, SqlTable

load_dotenv()

# Set up logging for scraping tweets
today = date.today().strftime("%Y-%m-%d")
log_file = f"logs/{today}.log"

logging.basicConfig(
    filename=log_file,
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s:%(filename)s:%(levelname)s:%(name)s:%(message)s",
)

user = TwitterUser(id=297549322, username="WesternWeightRm")
api_keys = TwitterApiKeys.from_env()
scraper = Scraper(user=user, api_keys=api_keys)

with SqlConnection.from_env().connect() as con:

    table = SqlTable(connection=con, name="fact_tweets")
    latest_tweet_id = table.last_observation()
    tweets = scraper.get_tweets(
        more_tweets=True, 
        max_results=100, 
        since_id=latest_tweet_id
    )

    if tweets:
        logging.info(f"Found new tweets for")
        for tweet in tweets:

            table.insert(
                "INSERT INTO fact_tweets (id, created_at, author_id, text) VALUES (%s, %s, %s, %s)",
                (tweet.id, tweet.created_at, tweet.author_id, tweet.text),
            )

        con.commit()

    else:
        logging.info(f"No new tweets for {user.username}")
