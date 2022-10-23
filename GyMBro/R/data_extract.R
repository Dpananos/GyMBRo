#' Extract data for training
#'
#' @param con Database Connection
#'
#' @return tibble of training data
#' @export
#'
#' @examples
#' # Not Run
wr_numbers <- function(con) {
  pre_covid <- dplyr::tbl(con, "PreCovidWR") %>%
    dplyr::select(created_at, WR) %>%
    dplyr::collect()

  post_covid <- dplyr::tbl(con, "PostCovidWR") %>%
    dplyr::select(created_at, WR) %>%
    dplyr::collect()

  special_periods <- dplyr::tbl(con, "SpecialPeriods") %>%
    dplyr::collect() %>%
    dplyr::mutate(dt = lubridate::ymd(date))


  wr <- pre_covid %>%
    dplyr::bind_rows(post_covid) %>%
    dplyr::mutate(dt = lubridate::date(lubridate::ymd_hms(created_at))) %>%
    dplyr::left_join(special_periods) %>%
    dplyr::select(-dt, -date) %>%
    dplyr::filter(!is.na(WR))

  return(wr)
}

#' Get Data For Forecasting
#'
#' @param con DB connection
#'
#' @return a dataframe
#' @export
#'
#' @examples
#' # Note Run
forecast_set <- function(con) {
  query <- "
          -- This query returns a data frame with the next 3 hours.
          -- So for example, if it were 3pm, it will return 4 - 6 pm on the current date
          -- It also joins those dates to the SpecialPeriods table to determine if the
          -- date is a special period
          -- The resulting data frame can be passed to the model directly.
          WITH RECURSIVE dates(date) AS (
            VALUES(datetime(strftime('%s', 'now') + (3600-strftime('%s', 'now') % 3600) , 'unixepoch', 'localtime'))
            UNION ALL
            SELECT datetime(date, '+1 hour')
            FROM dates
            WHERE date < datetime(strftime('%s', 'now') + (3600-strftime('%s', 'now') % 3600) + 2*3600, 'unixepoch', 'localtime')
          )
          SELECT
          dates.date as created_at,
          SpecialPeriods.period,
          SpecialPeriods.is_period,
          SpecialPeriods.days_to
          FROM dates
          left
          join SpecialPeriods on date(dates.date) = date(SpecialPeriods.date)
          where date(dates.date) <= date('now', 'localtime')
;
  "

  forecast_frame <- DBI::dbGetQuery(con, query) %>%
    dplyr::mutate(
      created_at = lubridate::ymd_hms(created_at,tz = "America/Toronto"
      )
    )

  return(forecast_frame)
}

#' Get Observations From Today
#'
#' @param con DB connection
#'
#' @return A dataframe
#' @export
#'
#' @examples
#' # Not Run
observed_set <- function(con) {
  query <- "
  select
    A.created_at,
    A.WR,
    B.days_to,
    B.Period,
    B.Is_Period
    from PostCovidWR A left join SpecialPeriods B on date(A.created_at) = date(B.date)
    where date(created_at) == date('now', 'localtime')
  "

  observed <- DBI::dbGetQuery(con, query) %>%
    dplyr::mutate(
      created_at = lubridate::ymd_hms(created_at,
        tz = "America/Toronto"
      )
    )

  return(observed)
}


#' Prediction Times For Model Plotting
#'
#' @param con DB connection
#'
#' @return a dataframe of times
#' @export
#'
#' @examples
#' # Not Run
prediction_times <- function(con) {
 
   tdy <- lubridate::today(tzone = "America/Toronto")

  tms <- seq(
    lubridate::ymd_hms(glue::glue("{tdy} 06:00:00"), tz = "America/Toronto"),
    lubridate::ymd_hms(glue::glue("{tdy} 23:00:00"), tz = "America/Toronto"),
    by = "1 hour"
  )

  special_periods <- dplyr::tbl(con, "SpecialPeriods") %>%
    dplyr::collect() %>%
    dplyr::mutate(dt = lubridate::date(date))

  prediction_frame <- data.frame(created_at = tms) %>%
    dplyr::mutate(
      dt = lubridate::date(created_at),
      created_at = lubridate::ymd_hms(created_at, tz = 'America/Toronto')
      ) %>%
    dplyr::left_join(special_periods) %>%
    dplyr::select(-dt, -date)

  return(prediction_frame)
}
