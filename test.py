import numpy as np
import pandas as pd
import sqlite3
import re
db_loc = 'database/Western_Tweet_Data.sqlite3'

def clean_text(text:str) -> str:
    
    # Replace non alpha-numeric chars
    text_no_alphanum = re.sub("[^0-9a-zA-Z]+", " ", text)

    # Replace multiple white spaces with single white space
    text_fewer_white = re.sub(" +", " ", text_no_alphanum)

    return text_fewer_white.upper()

def extract_text(text:str , slug:str) -> int:

    regex = re.compile(f'{slug} (\d+)')

    found = regex.findall(text)

    if len(found) == 1:
        return found[0]
    else:
        return np.NaN


with sqlite3.connect(db_loc) as con:

    query = 'select * from PostCovidWr'

    df = pd.read_sql(query, con)
    df['text2'] = df.text.apply(clean_text)
    df['WR'] = df.text2.apply(lambda x: extract_text(x, "WR"))

print(df.head(20))



