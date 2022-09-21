#' Fetch New Tweets
#'
#' @param con db connection
#' @param twitter_handle Twitter handle for fetching tweets
#' @param ... passed to rtweet::get_timeline
#'
#' @return dataframe of latest tweets
#' @export
#'
#' @examples
#' # NO RUN
fetch_new_tweets <- function(con, twitter_handle, ...) {

  # Fetch the latest tweet from the database
  existing_tweets <- dplyr::tbl(con, "PostCovidWr") %>%
    dplyr::mutate(created_at = dplyr::sql("datetime(created_at)")) %>%
    dplyr::arrange(dplyr::desc(created_at)) %>%
    head(1) %>%
    dplyr::collect()

  # Fetch tweets newer than this tweet

  latest_tweets <- rtweet::get_timeline(twitter_handle, since_id = existing_tweets, ...) %>%
    filter_retweets() %>% 
    dplyr::select(id, id_str, created_at, text) %>%
    dplyr::mutate(
      created_at = lubridate::with_tz(created_at, tz = "America/Toronto"),
      created_at = as.character(created_at)
    ) %>%
    # Fail safe in case there is an overlap
    dplyr::anti_join(existing_tweets)

  return(latest_tweets)
}

#' Filter out retweets from rtweet data
#'
#' @param data Dataframe
#'
#' @return dataframe
#' @export
#'
#' @examples
#' # Not Run
filter_retweets <- function(data) {
  
  # Determines if each tweet is a retweet by checking if the 
  # retweeted_status attribute has any information
  retweets <- purrr::map_lgl(data$retweeted_status, ~!all(is.na(unlist(.x))))
  
  filtered_data <- dplyr::filter(data, !retweets)
  
  return(filtered_data)
}


#' Write a dataframe to database
#'
#' @param data dataframe
#' @param con db connection
#'
#' @return NULL
#' @export
#'
#' @examples
#' # NORUN
write_to_db <- function(data, con) {
  if (nrow(data) == 0) {
  } else {
    DBI::dbWriteTable(con, "PostCovidWr", data, append = TRUE)
  }
}
