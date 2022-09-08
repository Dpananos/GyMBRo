library(tidyverse)
library(DBI)
library(dbplyr)
library(glue)



get_number<-function(text, slug){
  str_extract(text, regex(glue('(?<={slug}\\s)[0-9]+')))
}

my_function <- function(input_string, target) {
  
  str_extract(input_string, paste0(target, "\\D*\\d+")) |> str_extract("\\d+")
  
}

drv = RSQLite::SQLite()
con = DBI::dbConnect(drv, 'database/Western_Tweet_Data.sqlite3')

tbl(con, 'PostCovidWr') %>% 
  collect() %>% 
  mutate(created_at = ymd_hms(created_at)) %>% 
  arrange(desc(created_at))->f

view(f)

f %>% 
  transmute(
    # replace non-alphanumeric characters with white spaces
    text = str_replace_all(text, regex("[^[:alnum:] ]"), ' '),
    # replace multiple white spaces with a single white space
    text = str_replace(gsub("\\s+", " ", str_trim(text)), "B", "b"),
    # Turn all tweets to caps for matching
    text = str_to_upper(text)
  ) %>% 
  mutate(WR = get_number(text,'WR'),
         CM = get_number(text,'CM'),
         SPIN = get_number(text, 'SPIN')) 
  
  
DBI::dbDisconnect(con)
