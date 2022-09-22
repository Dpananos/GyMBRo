# GyMBRo: A Bot To Predict How Many People Are In My Gym

My gym [tweets out](https://twitter.com/WesternWeightRm) how many people are in the gym. This is good for an instantaneous understanding of how busy the gym is, but is fairly bad for planning when to go to the gym.

At the start of my Ph.D, I developed GyMBRo (Gym Monitoring By Robot) as a means of modelling the weight room numbers. I collect the tweet information and engineer some time features to predict how many people will be in the gym over the course of a day. This let's me (and other people who follow the bot on twitter) know what to expect in terms of gym utilization.

## Features

I use typical time features (month, day of week, time, etc.), but the most important features I've been able to engineer are "count down" features. The gym is most largely affected by holidays (e.g. Thanksgiving). In the days leading up to the holiday, many students will leave campus and return home. This affects the weight room too. Hence, I add features for which holiday is coming up, how many days are left until the holiday (max of 5), and an indicator for if the day is part of a special period (e.g. reading week). These count down features yield the largest reduction in loss (even more so than weather, which I stopped collecting because it only decreased the loss by 1 unit. It just wasn't worth my time).

## Loss

I use mean absolute error as my loss function

$$
\dfrac{1}{n}\sum_j \vert y_j - \hat{y}_j \vert
$$

because it as the nice interpretation of "GyMBRo is within MAE people on average". Additionally, the weight room numbers can be very long tailed and I don't want the model to take those observations too seriously.

## Data

I store the data in `database/Western_Tweet_Data.sqlite3`. I've split the data into two main tables: `PreCovidWR` and `PostCovidWr`. The gym stopped tweeting during Covid and started to tweet again in September 2022. I've also begun collecting all the tweeted out numbers (CM and SPIN) for eventual future modelling. I've also stored the dates at which the holidays and special periods occur in a table called `SpecialPeriods`.

## Model

I used a boosted tree, honestly because specifying the conditional mean and interaction in a linear model would be too hard. In particular, I use `LightGBM` because it can naturally account for categorical data without having to integer encode it myself *and* because missing data is also well handled. This saves me a lot of mental energy with feature engineering. Additionally, I find one hot encoding categorical variables to reduce performance appreciably, likely because of the tree's approach to randomly selecting features to split on within each node.

## Package

I've written a small package `{GyMBRo}` to house some helper functions.

## Why R and Not Python?

GymBRo was originally written in python and the twitter API in python pails in comparison to `{rtweet}`. I have no intention of rewriting this in python...again.
