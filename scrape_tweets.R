suppressMessages(library(logger))
suppressMessages(library(tidyverse))
suppressMessages(library(GyMBRo))
suppressMessages(library(here))
suppressMessages(library(rtweet))
# Connect to the database. Write to a new table where we keep the text of the
# tweet.  Will process later, and perhaps model all areas and not just WR.
suppressMessages(auth_as('credentials/GyMBRo.rds'))

log_info("----Pulling from database----")
drv <- RSQLite::SQLite()
con <- DBI::dbConnect(drv, "database/Western_Tweet_Data.sqlite3")


log_info("Fetching tweets")
twitter_handle <- "WesternWeightRm"
new_tweets <- suppressMessages(fetch_new_tweets(con, twitter_handle = twitter_handle))

# The `since_id` argument is what allows us to get new tweets only.
log_info("Found {nrow(new_tweets)} new tweets")

if (nrow(new_tweets) > 0) {
    log_success("Writing to Database")
    new_tweets %>% 
      mutate(
        cleaned_tweet = clean_tweet(text),
        WR = get_number(cleaned_tweet, 'WR'),
        CM = get_number(cleaned_tweet, 'CM'),
        SPIN = get_number(cleaned_tweet, "SPIN")
      ) %>% 
    write_to_db(con)
}

DBI::dbDisconnect(con)
log_info("-----------Exiting-----------")