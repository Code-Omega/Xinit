from iexfinance.stocks import get_historical_data, Stock, get_historical_intraday, get_earnings_today
from iexfinance import get_available_symbols
from iexfinance.utils.exceptions import IEXSymbolError

import pandas as pd
import numpy as np

from pytrends.request import TrendReq
from itertools import cycle
import time
from datetime import datetime
from pandas.tseries.offsets import BDay

import json

def get_ticker_info(ticker):
    stock_ep = Stock(ticker)

    data = {}

    try:
        comp_key_stats = stock_ep.get_key_stats()
        company_info = stock_ep.get_company()
        company_info['marketcap'] = comp_key_stats['marketcap']
        company_info['consensusEPS'] = comp_key_stats['consensusEPS']
        data['company_info'] = company_info

        earns = stock_ep.get_earnings()
        earning_dates = [datetime.strptime(x['EPSReportDate'],"%Y-%m-%d") for x in earns]
        actualEPSs = [x['actualEPS'] for x in earns]
        estimatedEPSs = [x['estimatedEPS'] for x in earns]
        data['earning_date'] = earning_dates[::-1]
        data['actual_EPS'] = actualEPSs[::-1]
        data['estimated_EPS'] = estimatedEPSs[::-1]

        date0 = datetime.today()
        wos = 14

        ts = get_historical_data(ticker, date0-BDay(wos), date0, output_format='pandas')
        ts_open = ts.open
        ts_open.index += pd.DateOffset(hours=9.5)
        ts_close = ts.close
        ts_close.index += pd.DateOffset(hours=16)
        ts = pd.concat([ts_open,ts_close])
        ts.sort_index(inplace = True)
        ts = ts.tz_localize('EST')
        data['ts'] = json.loads(ts.to_json(orient='split'))
    except:
        return ''

    return data

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
    trends_df.dropna(axis=0,inplace=True)
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
