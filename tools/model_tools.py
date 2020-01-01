import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
import pickle

from .data_tools import fetch_training
from .transforms import *

def make_validation_ix(X):

    # Model will be be validated using 
    # The most recent complete year's worth of data as the validation set
    # Rest is train
    # Pass the training data in order to perform the split
    # So base split on created_at column
    n_obs, _ = X.shape
    ix = np.arange(n_obs)

    max_year = pd.to_datetime('now').year

    # Need this to tell the model which part of X is training data and which is testing
    # Split doesn't happen until train time.
    slice_out_test = ix[(X.created_at.dt.year < max_year).values]

    training_ix = (X.created_at.dt.year<max_year-1).values
    training = ix[training_ix]

    validation_ix = (X.created_at.dt.year==max_year-1).values
    validation = ix[validation_ix]

    testing_ix = (X.created_at.dt.year==max_year).values
    testing = ix[testing_ix]


    return slice_out_test, [(training, validation)], testing

def FeatureEngineerTransformer():

    """
    Transformers concatenated together.  Does all the feature engineering for me.
    """

    feature_engineer = ColumnTransformer(
        [("TimeFeatures", TimeFeatureExtractor(), "created_at"),
        #  ("HolidayFeatures", HolidayFeatureExtractor(), "created_at"),
         ("SpecialFeatures", SpecialDayFeatureExtractor(), "created_at"),
         ("PrecipFeatures", OrdinalEncoder(categories=[["snow", "NoPrecip", "rain", "sleet"]]),["precipType"],)]
         ,remainder="passthrough")

    return feature_engineer

def load_model():

    with open('model.txt','rb') as f:
        model = pickle.load(f)

    return model

def score_model():

    X, y = fetch_training()
    ix = X.created_at.dt.year == pd.to_datetime("today").year
    X, y = X.loc[ix,], y[ix]
    model = load_model()
    score = model.score(X, y)
    return score


def compare_scores():

    month_names = (pd.date_range("2019-01-01", "2020-01-01", freq="M").month_name().tolist())

    X, y = fetch_training()
    training_ix = X.created_at.dt.year >= pd.to_datetime("today").year

    X.loc[training_ix, "Set"] = "Test"
    X.loc[~training_ix, "Set"] = "Train"
    X["Month"] = X.created_at.dt.month_name()
    X["y"] = y

    model = load_model()

    score_func = lambda X: -1 * model.score(X.drop("y", axis=1), X.y.values)
    scores = (X.groupby(["Month", "Set"]).apply(score_func)).unstack()

    return scores.loc[month_names,]