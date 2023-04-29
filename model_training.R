library(tidyverse)
library(tidymodels)
library(lubridate)
library(GyMBRo)
library(tidymodels)
library(bonsai)
library(here)
doParallel::registerDoParallel()
set.seed(0)

# Connect to the database to fetch the training data
drv <- RSQLite::SQLite()
con <- DBI::dbConnect(drv, "database/Western_Tweet_Data.sqlite3")

# Retrieve the training data.  The dates are stored as text in 
# SQLite, so need to convert them with the appropriate time zone.
wr <- con %>% 
      wr_numbers() %>% 
      mutate(created_at = ymd_hms(created_at, tz = 'America/Toronto'))

# Kill the connection, we don't need it from here.
DBI::dbDisconnect(con)

train_set <- wr %>% 
             filter(year(created_at) <=2020)

test_set <- wr %>% 
            filter(year(created_at) > 2020)

# Make a list of lists that house the walk forward validation
# Need an array for indicies.  Making the validation sets requires telling
# R which indicies are in train and which indicies are in test.
ix = seq(1, nrow(train_set))

# Split the validation by year
# 2014 vs rest
# 2014 - 2015 vs rest
# Leave 2019 and later as a test set.
# This code below creates a list of train/test indicies
split_ix<-map(2014:2018, ~{
  analysis <- ix[year(train_set$created_at) <= .x]
  assessment <- ix[year(train_set$created_at) > .x]
  list(analysis=analysis, assessment=assessment)
})

# Use the indicies and manual_rset to create an object which can be passed
# to tidymodels directly.
cv <- lapply(split_ix, make_splits, train_set) %>% 
      manual_rset(str_c('Split', 2015:2019))


# Create a helper function for feature engineering.
month_progress <- function(x) lubridate::day(x) / lubridate::days_in_month(x)

rec <- recipe(WR ~ ., data = train_set) %>% 
  step_date(created_at) %>%
  step_mutate_at(created_at, fn = list(month_progress = month_progress)) %>% 
  step_time(created_at, features = c('decimal_day'), keep_original_cols = F) %>% 
  prep()

model_spec <- boost_tree(
  trees = 1000, 
  tree_depth = tune(), min_n = tune(), 
  loss_reduction = tune(),                     ## first three: model complexity
  sample_size = tune(), mtry = tune(),         ## randomness
  learn_rate = tune(),                         ## step size
) %>% 
  set_engine("lightgbm") %>% 
  set_mode("regression")


model_grid <- grid_latin_hypercube(
  tree_depth(),
  min_n(),
  loss_reduction(),
  sample_size = sample_prop(),
  finalize(mtry(), train_set),
  learn_rate(),
  size = 1000
)

model_wf <- workflow() %>%
  add_recipe(rec) %>% 
  add_model(model_spec)

model_res <- tune_grid(
  model_wf,
  resamples = cv,
  grid = model_grid,
  metrics = metric_set(mae),
  control = control_grid(save_pred = TRUE)
)

best_fit <- select_best(model_res, "mae")

final_model <- finalize_workflow(
  model_wf,
  best_fit
) %>% 
  fit(filter(wr, created_at < today()))


dir.create(here('models', today()))

saveRDS(final_model, here('models', today(), 'model-wflw.rds'))
saveRDS.lgb.Booster(extract_fit_engine(final_model), here('models', today(), 'model-booster.rds'))


