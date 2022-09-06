suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(rtweet))
suppressPackageStartupMessages(library(lubridate))
library(logger)

# Connect to the database. Write to a new table where we keep the text of the
# tweet.  Will process later, and perhaps model all areas and not just WR.
log_info('----Pulling from database----')
con <- DBI::dbConnect(RSQLite::SQLite(), "database/Western_Tweet_Data.sqlite3")

twitter_handle <- 'WesternWeightRm'

# {rtweet} has functionality wherein I can pass a dataframe with a
# column `id` and it will get all tweets after that tweet.
log_info('Querying last tweet in database')
log_eval(
  last_tweet <- DBI::dbGetQuery(con, 'select * from PostCovidWr order by datetime(created_at) desc limit 1'),
level = "INFO"
)

log_info('Fetching tweets')
# The `since_id` argument is what allows us to get new tweets only.
weight_room_tweets <- get_timeline(twitter_handle, n=5000, since_id = last_tweet)

latest_tweets <- weight_room_tweets %>% 
  select(id, id_str, created_at, text) %>% 
  mutate(created_at = as.character(created_at))

log_info('Found {nrow(latest_tweets)} new tweets')

if (nrow(latest_tweets)>0) {
  # Do a basic check to see if all the dates are older than the latest tweet I have
  latest_db_tweet <- ymd_hms(last_tweet$created_at)
  fetched_tweets <- ymd_hms(latest_tweets$created_at)
  if (!all(fetched_tweets > latest_db_tweet)) {
    log_error('Fetched tweets not later than most recent tweet in database')
  }
  else {
    log_success('Writing to Database')
    DBI::dbWriteTable(con, 'PostCovidWr', latest_tweets, append=TRUE)
  }
}

DBI::dbDisconnect(con)
log_info('-----------Exiting-----------')
