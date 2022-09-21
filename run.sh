/usr/local/bin/Rscript scrape_tweets.R >> logging.log 2>&1
/usr/local/bin/Rscript make_plot.R >> logging.log 2>&1
/usr/local/bin/Rscript tweet.R >> logging.log 2>&1