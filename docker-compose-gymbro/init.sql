

CREATE TABLE IF NOT EXISTS fact_tweets(
    id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    author_id BIGINT,
    text VARCHAR(280),
    PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS fact_tweets_cleaned(
    id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    date DATE NOT NULL,
    author_id BIGINT,
    text VARCHAR(280),
    cleaned_text VARCHAR(280),
    WR BIGINT,
    CM BIGINT,
    SPIN BIGINT,
    PRIMARY KEY (id)
);