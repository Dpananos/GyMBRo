import logging
import time
from datetime import date, datetime
from dotenv import load_dotenv
from gymbro.scrape import Scraper, TwitterApiKeys, TwitterUser
from gymbro.connect import SqlConnection

# Set up logging for scraping tweets
today = date.today().strftime("%Y-%m-%d")
log_file = f"logs/{today}.log"

logger = logging.getLogger("tweepy")
logger.setLevel(logging.INFO)


logging.basicConfig(
    filename=log_file,
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s:%(filename)s:%(levelname)s:%(name)s:%(message)s",
)


def main():
    load_dotenv()

    user = TwitterUser(id=297549322, username="WesternWeightRm")
    api_keys = TwitterApiKeys.from_env()
    scraper = Scraper(user=user, api_keys=api_keys)

    connection = SqlConnection.from_env()
    with connection.connect_sqlalchemy().connect() as con:


        # Its more efficient to only grab tweets we haven't see before
        # Run a query to get the last tweet we have in our database
        # and pass that to the scraper
        latest_observation = con.execute(
            'SELECT "id" FROM fact_tweets order by created_at_utc desc LIMIT 1'
        )

        latest_observation = latest_observation.fetchall()

        if latest_observation:
            latest_tweet_id = latest_observation[0][0]
        else:
            latest_tweet_id = None

        tweets = scraper.get_tweets(
            more_tweets=True, max_results=100, since_id=latest_tweet_id
        )

        if tweets:
            logging.info(f"Found new tweets for {user.username}")
            for tweet in tweets:
                con.execute(
                    "INSERT INTO fact_tweets (id, created_at_utc, author_id, text) VALUES (%s, %s, %s, %s)",
                    (tweet.id, tweet.created_at, tweet.author_id, tweet.text),
                )

        else:
            logging.info(f"No new tweets for {user.username}")


if __name__ == "__main__":

    while True:
        now = datetime.now()

        if now.hour in range(6, 24):
            print('capturing')
            main()
            time.sleep(3600)
        else:
            time.sleep(3600)