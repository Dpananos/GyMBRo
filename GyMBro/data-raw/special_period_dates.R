library(lubridate)
library(here)
library(tidyverse)

create_leadup <- function(dt, period) {
  tseq <- seq(dt - days(5), dt - days(1), by = "1 day")
  frame <- tibble(
    date = tseq,
    period = period,
    days_to = rev(-seq_along(tseq))
  )

  return(frame)
}

fill_in_dates <- function(start, end, period) {
  tibble(
    date = seq(start, end, by = "1 day"),
    is_period = period
  )
}





file <- here("data-raw/special_periods_dates.csv")
special_period_dates <- read_csv(file)

drv <- RSQLite::SQLite()
con <- DBI::dbConnect(drv, "../database/Western_Tweet_Data.sqlite3")

dts <- read_csv("data-raw/special_periods_dates.csv")


tseq <- seq(
  min(date(dts$date)),
  max(date(dts$date)),
  by = "1 day"
)

dates <- tibble(date = tseq)

# Create leadups; just count down to each date
leadups <- map2_dfr(special_period_dates$date, special_period_dates$which_period, create_leadup)

# Create dates for fall reading breaks

fall_breaks <- special_period_dates %>%
  filter(grepl("Fall Study", which_period)) %>%
  mutate(yr = year(date)) %>%
  pivot_wider(id_cols = yr, names_from = which_period, values_from = date)

fall_break_days <- map2_dfr(fall_breaks$`Fall Study Break Start`, fall_breaks$`Fall Study Break End`, fill_in_dates, "Fall Study Break")

winter_breaks <- special_period_dates %>%
  filter(grepl("Reading Week", which_period)) %>%
  mutate(yr = year(date)) %>%
  pivot_wider(id_cols = yr, names_from = which_period, values_from = date)

reading_break_days <- map2_dfr(winter_breaks$`Reading Week Start`, winter_breaks$`Reading Week End`, fill_in_dates, "Reading Week")

# Add in the hoco



breaks <- bind_rows(reading_break_days, fall_break_days)


special_period_dates <- dates %>%
  left_join(leadups) %>%
  left_join(breaks) %>%
  mutate(date = as.character(date)) 


DBI::dbWriteTable(con, "SpecialPeriods", special_period_dates, overwrite=T)

DBI::dbDisconnect(con)
usethis::use_data(special_period_dates, overwrite = TRUE)
