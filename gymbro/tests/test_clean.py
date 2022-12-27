from gymbro.clean import clean_tweet, get_number_after_substring, TweetSlug
import pytest

raw_tweets = [
    "WR 35 🙊 CM 8 🙈  SPIN 1🐵",
    "WR 33   CM 9    SPIN 1",
    "WR 35   CM 4    SPIN 2",
    "WR 32   CM 3    SPIN 1",
    "WR 43🌟  CM 7🌲   Spin 3🎁",
    "WR: 31  CM: 4   Spin: 3",
    "WR 27   CM 5    Spin 2",
]

cleaned_tweets = [
    "WR 35 CM 8 SPIN 1",
    "WR 33 CM 9 SPIN 1",
    "WR 35 CM 4 SPIN 2",
    "WR 32 CM 3 SPIN 1",
    "WR 43 CM 7 SPIN 3",
    "WR 31 CM 4 SPIN 3",
    "WR 27 CM 5 SPIN 2",
]

WR_numbers = [35, 33, 35, 32, 43, 31, 27]
CM_numbers = [8, 9, 4, 3, 7, 4, 5]
SPIN_numbers = [1, 1, 2, 1, 3, 3, 2]


class TestCleanTweet:
    @pytest.mark.parametrize(
        "raw_tweet, cleaned_tweet", zip(raw_tweets, cleaned_tweets)
    )
    def test_clean_tweets(self, raw_tweet, cleaned_tweet):
        assert clean_tweet(raw_tweet) == cleaned_tweet


class TestGetNumberAfterSubstring:
    @pytest.mark.parametrize(
        "cleaned_tweet, wr_number", zip(cleaned_tweets, WR_numbers)
    )
    def test_wr_extract(self, cleaned_tweet, wr_number):
        assert get_number_after_substring(cleaned_tweet, TweetSlug.WR) == wr_number

    @pytest.mark.parametrize(
        "cleaned_tweet, cm_number", zip(cleaned_tweets, CM_numbers)
    )
    def test_cm_extract(self, cleaned_tweet, cm_number):
        assert get_number_after_substring(cleaned_tweet, TweetSlug.CM) == cm_number

    @pytest.mark.parametrize(
        "cleaned_tweet, spin_number", zip(cleaned_tweets, SPIN_numbers)
    )
    def test_spin_extract(self, cleaned_tweet, spin_number):
        assert get_number_after_substring(cleaned_tweet, TweetSlug.SPIN) == spin_number

    def test_no_slug_found(self):
        with pytest.raises(Exception):
            get_number_after_substring("WR 27 CM 5 SPIN 2", TweetSlug.CYCLE)

        with pytest.raises(Exception):
            get_number_after_substring("WR CM 5 SPIN 2", TweetSlug.WR)

        with pytest.raises(Exception):
            get_number_after_substring("CM 5 SPIN 2", TweetSlug.WR)

        with pytest.raises(Exception):
            get_number_after_substring("WR 12 SPIN 2", TweetSlug.CM)

        with pytest.raises(Exception):
            get_number_after_substring("WR 12 CM 5 SPN 12", TweetSlug.SPIN)
