#' @export 
load_model <- function(model_dir){
  
  model_files_dir <- list.files(path = model_dir, full.names = F)
  latest_model <- lubridate::ymd(model_files_dir) %>% 
                  max()
  model <- here::here(model_dir, latest_model, 'model-wflw.rds') %>% 
           readRDS()
  
  return(model)
}

#' @export 
fmt_dt <- function(x){
  # Helper function to remove zero padding from strftime  
  strftime(x, format = '%I %p') %>% 
    str_remove( "^0+")
}
