from tools.db_tools import update_tweet_db, update_weather_db
from tools.data_tools import fetch_wr
from tools.plot_tools import tweet, make_plot, fetch_predictions

update_tweet_db()
update_weather_db()
wr = fetch_wr()
preds = fetch_predictions()
make_plot(preds,wr)
tweet()
