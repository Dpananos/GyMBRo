from typing import List
from dataclasses import dataclass, field
import tweepy
import os


@dataclass
class TwitterUser:
    id: int
    username: str
    tweet_fields: List = field(
        default_factory=lambda: ["created_at", "author_id", "in_reply_to_user_id", "id"]
    )


@dataclass
class TwitterApiKeys:
    CLIENT_ID: str
    CLIENT_SECRET: str
    API_KEY: str
    API_SECRET: str
    BEARER_TOKEN: str
    ACCESS_TOKEN: str
    ACCESS_SECRET: str

    @classmethod
    def from_env(cls):
        
        return cls(
            CLIENT_ID=os.environ["CLIENT_ID"],
            CLIENT_SECRET=os.environ["CLIENT_SECRET"],
            API_KEY=os.environ["API_KEY"],
            API_SECRET=os.environ["API_SECRET"],
            BEARER_TOKEN=os.environ["BEARER_TOKEN"],
            ACCESS_TOKEN=os.environ["ACCESS_TOKEN"],
            ACCESS_SECRET=os.environ["ACCESS_SECRET"],
        )


class Scraper:

    """
    Authenticates with twitter API and scrapes twitter for tweets from a user.
    """

    def __init__(self, user: TwitterUser, api_keys: TwitterApiKeys):
        self.user = user
        self.api_keys = api_keys

    def scrape_data(self, client, **kwargs) -> List[tweepy.Tweet]:
        """
        Scrape the tweets from the user, returning a maximum of 100 tweets.
        Returns a tweepy response object.
        """

        response = client.get_users_tweets(
            id=self.user.id, tweet_fields=self.user.tweet_fields, **kwargs
        )

        return response

    def get_tweets(self, more_tweets=False, **kwargs) -> List[tweepy.Tweet]:

        client = tweepy.Client(self.api_keys.BEARER_TOKEN)

        # Initialize somewhere to store the tweets. Output of self.scrape_data 
        # is a response and not a list of tweets.
        output_data = []

        response = self.scrape_data(client=client, **kwargs)

        # If the response is not empty, append the list of tweets.
        if response.data:
            output_data.extend(response.data)

        # If we want more than the 100 limit, we need to repeatedly call
        # self.scrape_data until we get no more tweets.
        if more_tweets:
            while "next_token" in response.meta.keys():

                response = self.scrape_data(
                    client=client,
                    pagination_token=response.meta["next_token"],
                    **kwargs
                )

                if response.data:
                    output_data.extend(response.data)
                else:
                    break

        return output_data

def fetch_latest_tweet_id(cur):
    """
    Fetch the latest tweet id from the database.
    """
    cur.execute('SELECT "id" from fact_tweets order by created_at desc limit 1')

    latest_tweet_id = cur.fetchall()

    if latest_tweet_id:
        latest_tweet_id = latest_tweet_id[0]
    else:
        latest_tweet_id = None

    return latest_tweet_id