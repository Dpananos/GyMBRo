import pickle
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import tweepy

from .db_tools import load_keys
from .data_tools import fetch_weather
from .model_tools import load_model


def fetch_predictions():

    """
    Fetch model predictions as a dataframe.
    """

    # Data on which to predict
    preds = fetch_weather()

    model = load_model()

    predictions = model.predict(preds)

    preds["pred"] = predictions

    return preds

def make_plot(preds, wr):

    """
    Makes plot for tweeting.
    """

    now = pd.to_datetime("today")

    Hours = mdates.HourLocator(interval=4)
    fmt = mdates.DateFormatter("%-I %p")

    fig, ax = plt.subplots(figsize=(5, 3), dpi=300)
    ax.set_axisbelow(True)
    sns.despine(ax=ax)

    preds = preds.set_index("created_at")
    ax.plot(preds.index, preds.pred, linewidth=4, label="Predicted", color="#4F2683")
    # ax.set_ylim(0,150)

    # Might encounter problem if no tweets.
    if wr.shape[0] > 0:
        ax.scatter(
            wr.index,
            wr.WR,
            color="w",
            zorder=1000,
            label="Actual",
            edgecolor="k",
            linewidth=2,
        )

    ax.grid(True)
    ax.xaxis.set_major_locator(Hours)
    ax.xaxis.set_major_formatter(fmt)
    ax.set_xlabel("Time", size=12)
    ax.set_ylabel("People in Weight Room", size=12)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig("model_predictions.png")


def tweet():

    """
    Function to tweet predictions.

    Bot will also give a text description of predictions.

    E.g.

    Time Prediction
    2PM  100
    3PM  120
    4PM  125
    """

    # Fetch predictions
    preds = fetch_predictions().set_index("created_at")

    # Will be used to headline the tweet
    # E.g. Predictions for Saturday October 18 2018
    now = pd.to_datetime("today")
    # Format date to be used in tweet
    date = now.strftime("%A %b %d %Y")

    # Only get the next 4 hours of predictions
    preds = preds.loc[now:].iloc[:3, :]

    # Create tweet text
    # Data is in a dataframe which looks like [time, pred].
    # Format time to X PM
    preds.index = preds.index.strftime("%-I %p")
    preds = preds[["pred"]].round().astype("int")

    # Rename prediction column to prediction
    preds = preds.rename({"pred": "Prediction"}, axis=1)
    # Rename time column to Time
    preds.index.name = "Time"

    # This part creates the headline
    tweet = f"Predictions For {date}: \n\n"
    # This part adds the predictions
    tweet = tweet + preds.reset_index().to_string(index=False)

    # Result is

    # Predictions for Saturday October 18 2018
    # Time  Predictions
    # 2PM   100
    # 3PM   200
    # 4PM   100

    twitter_api_keys, _ = load_keys()
    _consumer_key = twitter_api_keys['consumer_key']
    _consumer_secret = twitter_api_keys['consumer_secret']
    _access_key = twitter_api_keys['access_key']
    _access_secret = twitter_api_keys['access_secret']
    auth = tweepy.OAuthHandler(_consumer_key, _consumer_secret)
    auth.set_access_token(_access_key, _access_secret)
    api = tweepy.API(auth)
    if np.logical_and(now.hour < 23, now.hour > 6):
        api.update_with_media("model_predictions.png", status=tweet)

