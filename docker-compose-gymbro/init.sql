

CREATE TABLE IF NOT EXISTS fact_tweets(
    id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    author_id BIGINT,
    TEXT VARCHAR(280),
    PRIMARY KEY (id)
);
