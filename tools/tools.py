import pandas as pd
import re
import holidays
import numpy as np
import sqlite3


def wr(x):

    '''
    Extract numbers from tweet
    '''
    X = re.sub(r'[^\w\s]',' ',x)
    split = X.lower().split()
    nums = [float(j) for j in split if j.isnumeric()]
    if len(nums)>0 and 'wr' in split:
        return max(nums)
    else:
        return -1

def holiday_name(t):

    '''
    Helper function used to get name of holiday from a date
    '''
    ca_holidays = holidays.Canada()
    try:
        name = ca_holidays[t]
    except KeyError:
        name = np.NaN
    return name


def get_days_leading(date, holiday):
    
    # Only inform model about 3 days leading up to the date
    lead_up_days = np.arange(-5,1)
    
    # Easily get dates by doing a timedelta_range
    diff_lead_up_days = pd.to_datetime(date) + pd.timedelta_range(start = '-5 day', end = '0 day')
    
    # Put it in a dataframe 
    lead_up_frame = pd.DataFrame({'date':diff_lead_up_days, 'days_until':lead_up_days, 'special_day': holiday})
    
    return lead_up_frame
    
def fill_in_period(exam_start, exam_end, period):
    
    period_dates = pd.date_range(exam_start, exam_end)
    
    period_frame = pd.DataFrame({'date':period_dates, 'period':period})
    
    return period_frame


def update_special_days_db(db_loc = 'database/Western_Tweet_Data.sqlite3'):

    H = pd.read_csv('holidays.csv', parse_dates=['date']).sort_values('date')

    fall_exams = (
                H[H.holiday.str.contains('Fall Exams')].
                assign(year = lambda x: x.date.dt.year).
                pivot(columns='holiday',index='year',values='date')
                )

    fall_exams_filled = []

    for start, end in zip(fall_exams['Fall Exams Start'], fall_exams['Fall Exams End']):
        fall_exams_filled.append(fill_in_period(start, end, 'Fall Exams'))
        
        
    fall_exams = pd.concat(fall_exams_filled)

    winter_exams = (
    H[H.holiday.str.contains('Winter Exams')].
    assign(year = lambda x: x.date.dt.year).
    pivot(columns='holiday',index='year',values='date'))

    winter_exams_filled = []

    for start, end in zip(winter_exams['Winter Exams Start'], winter_exams['Winter Exams End']):
        winter_exams_filled.append(fill_in_period(start, end, 'Winter Exams'))

    winter_exams = pd.concat(winter_exams_filled)

    reading_week = (
    H[H.holiday.str.contains('Reading')].
    assign(year = lambda x: x.date.dt.year).
    pivot(columns='holiday',index='year',values='date'))

    reading_week_filled = []

    for start, end in zip(reading_week['Reading Week Start'], reading_week['Reading Week End']):
        reading_week_filled.append(fill_in_period(start, end, 'Reading Week'))

    reading_week = pd.concat(reading_week_filled)

    fall_study = (
    H[H.holiday.str.contains('Fall Study')].
    assign(year = lambda x: x.date.dt.year).
    pivot(columns='holiday',index='year',values='date')
    )

    fall_study_filled = []

    for start, end in zip(fall_study['Fall Study Break Start'], fall_study['Fall Study Break End']):
        fall_study_filled.append(fill_in_period(start, end, 'Fall Study Break'))

    fall_study = pd.concat(fall_study_filled)

    period_effects = pd.concat((fall_exams, winter_exams, fall_study, reading_week)).sort_values('date')

    lead_ups = []

    for d, h in zip(H.date, H.holiday):
        lead_ups.append(get_days_leading(d,h))
        

    lead_ups = pd.concat(lead_ups)

    with sqlite3.connect(db_loc) as con:
        period_effects.to_sql('SpecialPeriods',index = False, con = con, if_exists='replace')
        lead_ups.to_sql('LeadUps', index = False, con = con, if_exists='replace')


