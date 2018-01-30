from flask import render_template
from app import app
from app import fetcher

# scrape
corpus,header,source = fetcher.scrape()

# summarize
_,_,doc_score,doc_rank,summaries,keywords,t_keywords = fetcher.summarize()

# setup iframe
iframe_dict = {
   "showChart":True,
   "locale":"en",
   "width":"100%",
   "height":"50%",
   "plotLineColorGrowing":"#3CBC98",
   "plotLineColorFalling":"#FF4A68",
   "gridLineColor":"#e9e9ea",
   "scaleFontColor":"#DADDE0",
   "belowLineFillColorGrowing":"rgba(60, 188, 152, 0.05)",
   "belowLineFillColorFalling":"rgba(255, 74, 104, 0.05)",
   "symbolActiveColor":"#F2FAFE",
   "tabs":[
      {
         "symbols":[
            {
               "s":"COINBASE:BTCUSD",
               "d":"Bitcoin / Dollar"
            },
            {
               "s":"OTC:GBTC",
               "d":"BITCOIN INVT TR"
            },
            {
               "s":"COINBASE:ETHUSD",
               "d":"Ethereum / Dollar"
            },
            {
               "s":"KRAKEN:BCHUSD",
               "d":"BCH / Dollar"
            },
            {
               "s":"BITTREX:XRPUSD",
               "d":"Ripple / Dollar"
            },
            {
               "s":"COINBASE:LTCUSD",
               "d":"Litcoin / Dollar"
            },
            {
               "s":"POLONIEX:USDTUSD",
               "d":"TETHER USD / DOLLAR"
            }
         ],
         "title":"News"
      },
      {
         "symbols":[
            {
               "s":"INDEX:SPX",
               "d":"S&P 500"
            },
            {
               "s":"INDEX:IUXX",
               "d":"Nasdaq 100"
            },
            {
               "s":"INDEX:DOWI",
               "d":"Dow 30"
            },
            {
               "s":"INDEX:NKY",
               "d":"Nikkei 225"
            },
            {
               "s":"NASDAQ:AAPL",
               "d":"Apple"
            },
            {
               "s":"NASDAQ:GOOG",
               "d":"Google"
            }
         ],
         "title":"Equities"
      },
      {
         "symbols":[
            {
               "s":"CME_MINI:ES1!",
               "d":"E-Mini S&P"
            },
            {
               "s":"CME:E61!",
               "d":"Euro"
            },
            {
               "s":"COMEX:GC1!",
               "d":"Gold"
            },
            {
               "s":"NYMEX:CL1!",
               "d":"Crude Oil"
            },
            {
               "s":"NYMEX:NG1!",
               "d":"Natural Gas"
            },
            {
               "s":"CBOT:ZC1!",
               "d":"Corn"
            }
         ],
         "title":"Commodities"
      },
      {
         "symbols":[
            {
               "s":"CME:GE1!",
               "d":"Eurodollar"
            },
            {
               "s":"CBOT:ZB1!",
               "d":"T-Bond"
            },
            {
               "s":"CBOT:UD1!",
               "d":"Ultra T-Bond"
            },
            {
               "s":"EUREX:GG1!",
               "d":"Euro Bund"
            },
            {
               "s":"EUREX:II1!",
               "d":"Euro BTP"
            },
            {
               "s":"EUREX:HR1!",
               "d":"Euro BOBL"
            }
         ],
         "title":"Bonds"
      },
      {
         "symbols":[
            {
               "s":"FX:EURUSD"
            },
            {
               "s":"FX:GBPUSD"
            },
            {
               "s":"FX:USDJPY"
            },
            {
               "s":"FX:USDCHF"
            },
            {
               "s":"FX:AUDUSD"
            },
            {
               "s":"FX:USDCAD"
            }
         ],
         "title":"Forex"
      }
   ],
   "utm_source":"www.tradingview.com",
   "utm_medium":"widget",
   "utm_campaign":"marketoverview"
}

#print("https://s.tradingview.com/marketoverviewwidgetembed/#"+urllib.parse.quote(str(json.dumps(iframe_dict))))

#---------------------------------------------------------------------------------------------------
#                   refreshing & threading
#---------------------------------------------------------------------------------------------------

import threading

import time
import datetime
from slackclient import SlackClient

BOT_NAME = 'xibot'
BOT_ID = 'U7MC33TL1'
WEBSOCKET_DELAY = 10
slack_client = SlackClient("xoxb-259411129681-GdhoO4YDGsTolR9zSTVR8ndP")

def xibot():
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            response = """
            <h1>Hello from heroku</h1>
            <img src="http://loremflickr.com/600/400" />
            """

            slack_client.api_call("chat.postMessage", channel='xinit',
                              text=response, as_user=True)
            time.sleep(WEBSOCKET_DELAY)

t = threading.Thread(target=xibot)
#t.start()

#---------------------------------------------------------------------------------------------------
#                   Web
#---------------------------------------------------------------------------------------------------

@app.route('/')
@app.route('/index')
def index():
	sources = {'name': 'CNBC, Bloomberg View, and Seeking Alpha',
			  'length': len(corpus),
			  'keywords': "; ".join([x[0] for x in t_keywords])}
	posts = [{'title': header[i][0],
			  'content': "<br /><br />".join([x[0].replace('\n',' ') for x in summaries[i]]),
			  'keywords': "; ".join([x[0] for x in keywords[i]]),
			  'condense_rate': "{:.3%}".format(sum([len(x[0]) for x in summaries[i]])/len(corpus[i])),
              'source': source[i],
              'score': doc_score[i],
			  'link': header[i][1]} for i in doc_rank]
	iframe_src = {'tv' : "https://s.tradingview.com/marketoverviewwidgetembed/#"+urllib.parse.quote(str(json.dumps(iframe_dict)))}
	return render_template("index.html",
    					   title='Home',
                           sources=sources,
                           posts=posts,
                           iframe_src=iframe_src)
