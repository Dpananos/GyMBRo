import tweepy
import pytest
from datetime import datetime
from gymbro.connect import SqlConnection
from gymbro.scrape import Scraper, TwitterApiKeys, TwitterUser, fetch_latest_tweet_id


user = TwitterUser(id=297549322, username='WesternWeightRm')
api_keys = TwitterApiKeys.from_env()
scraper = Scraper(user=user, api_keys=api_keys)


class TestScraper:
    def test_fetch_latest_tweet_id(self):

        # Connect to a test database where I have kept tweets from 2022-09-08
        with SqlConnection.from_env(file_path='.test.env').connect() as con:
            cur = con.cursor()
            latest_tweet_id = fetch_latest_tweet_id(cur)
            cur.close()
            assert latest_tweet_id == 1568020944689692672

    @pytest.mark.parametrize("max_results, expected_length", zip([10, 20, 100], [10, 20, 100]))
    def test_scrape_data_length(self, max_results, expected_length):
        # Test that the scrape_data method returns a list of tweets
        client = tweepy.Client(api_keys.BEARER_TOKEN)

        response = scraper.scrape_data(client=client, max_results=max_results)

        assert len(response.data) == expected_length

    def test_get_tweets_since_id(self):

        client = tweepy.Client(api_keys.BEARER_TOKEN)

        response = scraper.scrape_data(client=client, max_results=100, since_id=1568020944689692672)

        for tweet in response.data:
            assert tweet.created_at.date() > datetime(2022, 9, 8).date()