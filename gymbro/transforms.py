import holidays
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import sqlite3

from .tools import holiday_name

class TimeFeatureExtractor(BaseEstimator, TransformerMixin):

    '''
    Sklearn transformer for time features. Used in machine learning pipeline.
    The transformer's fit method returns the an object of type
    TimeFeatureExtractor.  Consequently, the method can only be used via the
    fit_transform method.

    Currently returns:
        - Year
        - Month
        - Week
        - Day
        - Month Progress
        - Year Progress
        - Time (Fractional Hours)
    '''

    def __init__(self):

        return None

    def transform(self, t, *_):

        #Accepts a pandas Series as input.

        year = t.dt.year
        month = t.dt.month
        week = t.dt.weekofyear
        day = t.dt.dayofweek
        month_progress = t.dt.day/t.dt.days_in_month
        year_progress = t.dt.day/365.25
        time = t.dt.hour + t.dt.minute/60


        time_data =  pd.DataFrame({'year':year,
                                   'month':month,
                                   'week': week,
                                   'day': day,
                                   'month_progress': month_progress,
                                   'year_progress': year_progress,
                                   'time': time}
                                 )

        self.feature_names = time_data.columns

        return time_data

    def get_feature_names(self):

        #This can be used down the road to return feature names in a
        #column transformer
        return self.feature_names


    def fit(self, *_):

        return self



class HolidayFeatureExtractor(BaseEstimator, TransformerMixin):

    '''
    Sklearn transformer to deal with holidays.

    Currently returns:
        is_holiday: Numeric coding for holidays.  -1 if day is not holiday
        days_to_holiday:  Counting down days to/from holiday.  NaN if holiday
                          is more than a week away.

    '''

    def __init__(self):

        return None

    def transform(self, t, *_):

        #Takes as input a pandas series.

        #Names of holidays
        holiday_names = ['Family Day',
                            'Good Friday',
                            'Victoria Day',
                            'Canada Day',
                            'Civic Holiday',
                            'Labour Day',
                            'Thanksgiving',
                            "New Year's Day",
                            'Boxing Day (Observed)',
                            "New Year's Day (Observed)",
                            'Canada Day (Observed)']

        #Set up a dataframe to left join to
        holi = pd.DataFrame({'times':t})
        holi['dates']= holi.times.dt.round('D')

        #Determine days to holidays
        #Make max date a week later than actual max date because of a bug when computing
        #days to next holiday.

        #Days in the dataset
        date_min = t.dt.date.min()
        date_max = t.dt.date.max() + pd.Timedelta('7 day')
        date_range = pd.date_range(date_min, date_max)
        date_range = pd.DataFrame({'dates':date_range})

        #Get the name of the holiday
        date_range['is_holiday'] = date_range.dates.apply(holiday_name)

        #Now compute days to and after holiday
        date_range['grouper'] = date_range['is_holiday'].notnull().cumsum()
        date_range['aft'] = date_range.groupby('grouper').cumcount()
        date_range['bef'] = date_range.groupby('grouper').cumcount(ascending=False) + 1
        date_range['days_to_holiday'] = date_range[['aft', 'bef']].min(axis=1)
        date_range.loc[date_range['bef'] == date_range['days_to_holiday'], 'days_to_holiday'] *= -1

        mask = date_range['is_holiday'].ffill(limit=7).bfill(limit=6).isnull()
        date_range.loc[mask, 'days_to_holiday'] = pd.np.nan

        date_range = date_range[['dates', 'is_holiday', 'days_to_holiday']]

        #Combine the two dataframes
        holiday_data = holi.merge(date_range, how = 'left').drop(['dates','times'], axis = 1)

        #Back and forward fill so we know which holidays are coming up/past
        back_holiday_names = holiday_data.loc[holiday_data.days_to_holiday<=0,'is_holiday'].fillna(method = 'bfill')
        holiday_data.loc[holiday_data.days_to_holiday<=0,'is_holiday']=back_holiday_names

        forward_holiday_names = holiday_data.loc[holiday_data.days_to_holiday>=0,'is_holiday'].fillna(method = 'ffill')
        holiday_data.loc[holiday_data.days_to_holiday>=0,'is_holiday']=forward_holiday_names

        #Finally, turn holidays into a numeric
        holiday_data['is_holiday'] = pd.Categorical(holiday_data.is_holiday,categories=holiday_names).codes

        self.feature_names = holiday_data.columns

        return holiday_data

    def get_feature_names(self):

        return self.feature_names


    def fit(self, *_):

        return self


class SpecialDayFeatureExtractor(BaseEstimator, TransformerMixin):

    #Still experimental and requires work!
    def __init__(self, db_con='database/Western_Tweet_Data.sqlite3'):
        self.db_con= db_con

        return None
    
    def transform(self, t, *_):

        special_days = ['Winter Classes Start', 
                        'Reading Week Start', 
                        'Reading Week End',
                        'Winter Classes End',
                        'Winter Exams Start',
                        'Winter Exams End',
                        'Canada Day',
                        'Civic Holiday',
                        'Fall Classes Start',
                        'Thanksgiving',
                        'Fall Study Break Start',
                        'Fall Study Break End',
                        'Fall Classes End',
                        'Fall Exams Start',
                        'Fall Exams End']

        special_periods = ['Winter Exams','Fall Exams','Reading Week','Fall Study Break']

        with sqlite3.connect(self.db_con) as con:
            period_effects= pd.read_sql('select * from SpecialPeriods',con=con, parse_dates=['date'])
            lead_ups= pd.read_sql('select * from LeadUps', con = con, parse_dates=['date']).sort_values(['date','days_until'], ascending = [True,False])
            lead_ups = lead_ups.groupby('date', as_index = False).last()



        dates = pd.DataFrame({'date':pd.to_datetime(t.dt.date)})

        dates = dates.merge(period_effects, how = 'left').merge(lead_ups, how = 'left')

        dates['period'] = pd.Categorical(dates.period, categories = special_periods).codes
        dates['special_day'] = pd.Categorical(dates.special_day, categories=special_days).codes
        dates = dates.drop('date', axis = 'columns')
        return dates
    
    def fit(self, *_):
        return self
