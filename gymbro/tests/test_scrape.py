import tweepy
import pytest
from datetime import datetime
from gymbro.connect import SqlConnection
from gymbro.scrape import Scraper, TwitterApiKeys, TwitterUser


user = TwitterUser(id=297549322, username='WesternWeightRm')
api_keys = TwitterApiKeys.from_env()
scraper = Scraper(user=user, api_keys=api_keys)


class TestScraper:

    @pytest.mark.parametrize("max_results, expected_length", zip([10, 20, 100], [10, 20, 100]))
    def test_scrape_data_length(self, max_results, expected_length):
        # Test that the scrape_data method returns a list of tweets
        client = tweepy.Client(api_keys.BEARER_TOKEN)

        response = scraper.scrape_data(client=client, max_results=max_results)

        assert len(response.data) == expected_length