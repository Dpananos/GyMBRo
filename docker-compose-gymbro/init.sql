

CREATE TABLE IF NOT EXISTS fact_tweets(
    id BIGINT NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL,
    author_id BIGINT,
    text VARCHAR(280),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS pre_covid_weightroom(
    id BIGINT NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL,
    WR BIGINT,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS fact_tweets_cleaned(
    id BIGINT NOT NULL,
    date DATE NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL,
    created_at_est TIMESTAMPTZ NOT NULL,
    author_id BIGINT,
    text VARCHAR(280),
    cleaned_text VARCHAR(280),
    WR BIGINT,
    CM BIGINT,
    SPIN BIGINT,
    PRIMARY KEY (id)
);