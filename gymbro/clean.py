import re
from typing import List
from enum import Enum


class TweetSlug(Enum):
    WR = "WR"
    CM = "CM"
    SPIN = "SPIN"


class NoSlugFoundError(Exception):
    """
    Exception raised when no slug is found in a tweet.
    """

    def __init__(self, cleaned_text, slug):
        self.cleaned_text = cleaned_text
        self.slug = slug
        self.message = f"No slug {self.slug} found in tweet '{self.cleaned_text}'"
        super().__init__(self.message)


def clean_tweet(text: str) -> str:

    """
    Clean tweet text by removing non-alphanumeric characters and
    replacing multiple whitespace with single whitespace. Removes emojis too.
    """

    # Remove non-alphanumeric characters form text
    cleaned_text = re.sub("[^0-9a-zA-Z ]+", " ", text)

    # Replace multiple whitespace with single whitespace
    cleaned_text = re.sub("\\s+", " ", cleaned_text).strip()

    # Return text in uppercase
    cleaned_text = cleaned_text.upper()

    return cleaned_text


def get_number_after_substring(cleaned_text: str, slug: TweetSlug) -> int:

    """
    Get number after a substring (e.g. WR) in a string.
    Used for extracting how many users are in each room from a tweet.
    """

    # TODO: Add resiliency to this function. If the slug is not found,
    # look for a fuzzy match. If no fuzzy match is found, raise an error.
    # Get the number after the substring using regex
    try:
        number = re.search(f"{slug.value} (\\d+)", cleaned_text).group(1)
        return int(number)
    except AttributeError:
        raise NoSlugFoundError(cleaned_text=cleaned_text, slug=slug.value)
