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

observed <- observed_set(con)
predictions <- prediction_times(con) %>% 
               bind_cols(
                 round(predict(model, new_data=.))
               )


log_info("----Creating Plot----")
# Add geoms to the plot
base_plot <- predictions %>% 
  ggplot(aes(created_at, .pred )) + 
  geom_line(aes(color='Predicted'), size=1)

if (nrow(observed) > 0){
  base_plot = base_plot + 
    geom_point(data=observed, aes(created_at, WR, shape="Observed WR Numbers"), color='black', fill='white')
}


# Now just do some simple styling.
full_plot<-base_plot + 
  scale_shape_manual(values = c(21)) + 
  scale_color_manual(values = c('#4F2683')) + 
  scale_y_continuous(limits = c(0, NA)) + 
  scale_x_datetime(labels = fmt_dt, date_breaks = '4 hours') + 
  labs(
    # subtitle = 'How Many People Will Be In The Weight Room?',
    x = 'Time',
    y = 'People in Weight Room',
    color = '',
    shape = ''
  ) +
  theme_classic() + 
  theme(
    panel.grid.major = element_line(),
    panel.grid.minor = element_line(size = 0.125),
    aspect.ratio = 1/2,
    legend.text = element_text(size = 8),
    legend.position = 'top',
    plot.margin=grid::unit(c(1, 1, 1, 1), "mm")
  )



log_success("----Saving Plot----")
ggsave("predicted.png", plot=full_plot, height = 3, width = 3 * 1.61, dpi = 240)

DBI::dbDisconnect(con)