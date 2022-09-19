#' Extract data for training
#'
#' @param con Database Connection
#'
#' @return tibble of training data
#' @export
#'
#' @examples
#' #Not Run
wr_numbers <- function(con){
  
  pre_covid <- dplyr::tbl(con, 'PreCovidWR') %>% 
               dplyr::select(created_at, WR) %>% 
               dplyr::collect()
  
  post_covid <- dplyr::tbl(con, 'PostCovidWR') %>% 
                dplyr::select(created_at, WR) %>% 
                dplyr::collect()
  
  special_periods <- dplyr::tbl(con, "SpecialPeriods") %>% 
                     dplyr::collect() %>% 
                     dplyr::mutate(dt = lubridate::ymd(date))
  
  
  wr <- pre_covid %>% 
    dplyr::bind_rows(post_covid) %>% 
    dplyr::mutate(dt = lubridate::date(lubridate::ymd_hms(created_at))) %>% 
    dplyr::left_join(special_periods) %>% 
    dplyr::select(-dt, -date)
  
  return(wr)
  
}