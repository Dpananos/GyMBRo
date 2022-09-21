suppressMessages(library(tidyverse))
suppressMessages(library(lubridate))
suppressMessages(library(tidymodels))
suppressMessages(library(lightgbm))
suppressMessages(library(GyMBRo))
suppressMessages(library(here))
suppressMessages(library(rtweet))
suppressMessages(library(logger))

log_info("----Connecting to database----")
drv <- RSQLite::SQLite()
con <- DBI::dbConnect(drv, "database/Western_Tweet_Data.sqlite3")

model <- load_model(model_dir = 'models')
# This is only because I'm using a lightgbm.  There is apparently
# an issue with the booster being saved by tidymodels
model_files_dir <- list.files(path = 'models', full.names = F)
latest_model <- max(ymd(model_files_dir))
model$fit$fit$fit <- readRDS.lgb.Booster(here('models', latest_model,'model-booster.rds'))

fs <- forecast_set(con)

if(nrow(fs) > 0) {
  
  prediction <- fs %>% 
    bind_cols(predict(model, .)) %>% 
    mutate(.pred = round(.pred),
           Time = fmt_dt(created_at)) %>% 
    rename(Prediction = .pred) %>% 
    select(Time, Prediction) %>% 
    knitr::kable("simple") %>% 
    format() %>% 
    paste0(collapse = "\n")
  
  
  tweet_text <- glue::glue("Predictions for {today()}") %>% 
                str_c(prediction, sep = "\n\n") 
  
  auth_as('credentials/GyMBRo.rds')
  
  log_info("----Tweeting----")
  post_tweet(status = tweet_text, media = c('predicted.png'), media_alt_text = c(''))
  
  
}

DBI::dbDisconnect(con)