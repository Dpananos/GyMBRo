import re

def clean_text(text:str) -> str:
    
    # Replace non alpha-numeric chars
    text_no_alphanum = re.sub("[^0-9a-zA-Z]+", " ", text)

    # Replace multiple white spaces with single white space
    text_fewer_white = re.sub(" +", " ", text_no_alphanum)

    return text_fewer_white.upper().strip()

def extract_text(text:str , slug:str) -> int:

    regex = re.compile(f'{slug} (\d+)')

    found = regex.findall(text)

    if len(found) == 1:
        return found[0]
    else:
        return 'NaN'