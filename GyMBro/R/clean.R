#' Extract number from tweet
#'
#' @param text cleaned text
#' @param slug slug to grab number from
#'
#' @return int
#' @export
#'
#' @examples
#' # NOT RUN 
get_number<-function(text, slug){
  # Extracts number after slug
  # TODO: This is not great, fix warning later
  re = suppressWarnings(stringr::regex(glue::glue('(?<={slug}\\s)[0-9]+')))
  
  num <- as.numeric(stringr::str_extract(text, re))
  
  return(num)
}

#' Clean tweet
#'
#' @param tweet Text to clean
#'
#' @return cleaned text
#' @export
#'
#' @examples
#' # NOT RUN
clean_tweet <- function(tweet){
  
  only_alphanum <- stringr::str_replace_all(tweet, stringr::regex("[^[:alnum:] ]"), ' ')
  stripped_tweet <- stringr::str_squish(only_alphanum)
  single_white_space <- stringr::str_replace_all(stripped_tweet, "\\s+", " ")
  upper_cleaned <- stringr::str_to_upper(single_white_space)
  
  return(upper_cleaned)
}