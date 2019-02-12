# from iexfinance.stocks import get_historical_data, Stock, get_historical_intraday
# from iexfinance import get_available_symbols
# from iexfinance.utils.exceptions import IEXSymbolError

import pandas as pd
import numpy as np

# import matplotlib.pyplot as plt
# from datetime import datetime
# from collections import defaultdict, OrderedDict
# import pickle

from pytrends.request import TrendReq
from itertools import cycle
import time

def get_google_trends(mongo, num = 6):
    page_data = mongo.db.processed_feeds.find_one()

    corpus = page_data['corpus']
    #t_keywords = page_data['t_keywords']
    #keywords = [x[0] for x in t_keywords]
    key_assets = page_data['key_assets']
    keywords = [x for x in key_assets]

    # XXX: testing
    #print(len(keywords))
    keywords = keywords[:min(num,len(keywords))]

    pytrends = TrendReq(hl='en-US', tz=360)
    #pytrends.build_payload(keywords, cat=0, timeframe='now 1-d', geo='', gprop='')
    #trends_df.drop('isPartial',1,inplace=True)
    trends_dfs = []
    for k in keywords:
        pytrends.build_payload([k], cat=0, timeframe='now 1-d', geo='', gprop='')
        tdf = pytrends.interest_over_time()
        tdf.drop('isPartial',1,inplace=True)
        trends_dfs.append(tdf)
        #print(len(tdf))
        #time.sleep(1)
    trends_df = pd.concat(trends_dfs,axis=1)
    trends_df.dropna(axis=0,inplace=False)
    #trends_table = trends_df.to_html()

    x_axis = list(trends_df.index.strftime("%H:%M"))
    series_names = list(trends_df.columns.values)
    values = trends_df.values.transpose().tolist()
    color_palette = cycle(['#4c72b0', '#55a868', '#c44e52', '#8172b2', '#ccb974', '#64b5cd'])
    colors = [next(color_palette) for _ in range(num)]

    # STORE RESULTS
    mongo.db.current_trends.drop()
    mongo.db.current_trends.insert(
        {'keywords' : keywords,
         'x_axis' : x_axis,
         'series_names' : series_names,
         'values' : values,
         'colors' : colors
         })
