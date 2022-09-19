library(tidyverse)
library(tidymodels)
library(lubridate)
library(GyMBRo)
library(tidymodels)
library(bonsai)

drv <- RSQLite::SQLite()
con <- DBI::dbConnect(drv, "database/Western_Tweet_Data.sqlite3")

wr <- con %>% 
      wr_numbers() %>% 
      mutate(created_at = ymd_hms(created_at, tz = 'America/Toronto'))

DBI::dbDisconnect(con)

train_set <- filter(wr, year(created_at) < 2019) %>% 
  as_tibble() %>% 
  mutate(created_at = ymd_hms(created_at))

test_set <- filter(wr, year(created_at) >=2019) %>% 
  as_tibble() %>% 
  mutate(created_at = ymd_hms(created_at))

# Make a list of lists that house the walk forward validation
ix = seq(1, nrow(train_set))


split_ix<-map(2014:2017, ~{
  analysis <- ix[year(train_set$created_at) <= .x]
  assessment <- ix[year(train_set$created_at) > .x]
  list(analysis=analysis, assessment=assessment)
})

cv <- lapply(split_ix, make_splits, train_set) %>% 
      manual_rset(str_c('Split', 2015:2018))

month_progress <- function(x) lubridate::day(x) / lubridate::days_in_month(x)



rec <- recipe(WR ~ ., data = train_set) %>% 
  step_date(created_at) %>%
  step_mutate_at(created_at, fn = list(month_progress = month_progress)) %>% 
  step_time(created_at, features = c('decimal_day'), keep_original_cols = F) %>% 
  prep()

xgb_spec <- boost_tree(
  trees = 1000, 
  tree_depth = tune(), min_n = tune(), 
  loss_reduction = tune(),                     ## first three: model complexity
  sample_size = tune(), mtry = tune(),         ## randomness
  learn_rate = tune(),                         ## step size
) %>% 
  set_engine("lightgbm") %>% 
  set_mode("regression")

xgb_grid <- grid_latin_hypercube(
  tree_depth(),
  min_n(),
  loss_reduction(),
  sample_size = sample_prop(),
  finalize(mtry(), train_set),
  learn_rate(),
  size = 250
)

xgb_wf <- workflow() %>%
  add_recipe(rec) %>% 
  add_model(xgb_spec)

doParallel::registerDoParallel()

set.seed(234)
xgb_res <- tune_grid(
  xgb_wf,
  resamples = cv,
  grid = xgb_grid,
  metrics = metric_set(mae),
  control = control_grid(save_pred = TRUE)
)

best_fit <- select_best(xgb_res, "mae")

final_xgb <- finalize_workflow(
  xgb_wf,
  best_fit
) %>% 
  fit(filter(wr, created_at < today()))

saveRDS(final_xgb, "lgbm_wflw.rds")
saveRDS.lgb.Booster(extract_fit_engine(final_xgb), "lgbm_booster.rds")
