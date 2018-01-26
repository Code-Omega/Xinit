from flask import render_template
from app import app

import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import feedparser
import urllib
from bs4 import BeautifulSoup
import json

#---------------------------------------------------------------------------------------------------
#                   Source                                      begins
#---------------------------------------------------------------------------------------------------

CNBC_feed_url = 'https://www.cnbc.com/id/10000664/device/rss/rss.html'
dCNBC = feedparser.parse(CNBC_feed_url)

SA_feed_url = 'https://seekingalpha.com/feed.xml'
dSA = feedparser.parse(SA_feed_url)

BVML_feed_url = 'https://www.bloomberg.com/view/rss/contributors/matt-levine.rss'
dBVML = feedparser.parse(BVML_feed_url)

#---------------------------------------------------------------------------------------------------
#                   Source                                      ends
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#                   Scraping                                    begins
#---------------------------------------------------------------------------------------------------

def get_CNBC_text(url):
    """
    return the title and the text of the article
    at the specified url
    """
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page,"lxml")
    # scrape for content
    # for CNBC only
    content = soup.find("div", {"id": "article_body"})
    if not content:
        content = soup.find("div", {"class": "story_listicle_body"})
    if not content:
        content = soup.find("div", {"id": "slideshow-text"})
        if content:
            text = [p.text for p in content.find_all('p')]
            slideNum = int(soup.find("span", {"class": "slidecount"}).text.split("/")[1])
            for slideIdx in range (2,slideNum) :
                next_page = urllib.request.urlopen(url+'?slide='+str(slideIdx)).read()
                next_soup = BeautifulSoup(next_page,"lxml")
                content = next_soup.find("div", {"id": "slideshow-text"})
                text.extend([p.text for p in content.find_all('p')])
            return text
    if not content:
         return soup.title.string
    # get text
    text = [p.text for p in content.find_all('p')]
    #return soup.title.text, text
    return text

def get_SA_text(url):
    """
    return the title and the text of the article
    at the specified url
    """
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(request)
    page = page.read().decode('utf8')
    soup = BeautifulSoup(page,"lxml")
    # for seekingalpha only
    header_content = soup.find('article').find("header")
    body_content = soup.find("div", {"id": "a-body"})
    text = [body_content.text]
    #return soup.title.text, text
    return text

def get_BV_text(url):
    """
    return the title and the text of the article
    at the specified url
    """
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(request)
    page = page.read().decode('utf8')
    soup = BeautifulSoup(page,"lxml")
    # for Bloomberg View only
    body_content = soup.find("section", {"class": "main-column"})
    text = body_content.findAll(text=True)
    #return soup.title.text, text
    return text

articles_per_source = 10

corpus = []
header = []
source = []
for post in dCNBC.entries[:articles_per_source]:
    #print (post.title + ": " + post.link + "\n")
    content = get_CNBC_text(post.link)
    corpus.append(" ".join(content))
    header.append([post.title,post.link])
    source.append("CNBC")

for post in dSA.entries[:articles_per_source]:
    #print (post.title + ": " + post.link + "\n")
    content = get_SA_text(post.link)
    corpus.append(" ".join(content))
    header.append([post.title,post.link])
    source.append("Seeking Alpha")
    
for post in dBVML.entries[:articles_per_source]:
    #print (post.title + ": " + post.link + "\n")
    content = get_BV_text(post.link)
    corpus.append(" ".join(content))
    header.append([post.title,post.link])
    source.append("Bloomberg View")

#---------------------------------------------------------------------------------------------------
#                   Scraping                                    ends
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#                   Summarizing                                 begins
#---------------------------------------------------------------------------------------------------

vectorizer = TfidfVectorizer(input = 'content',
                             norm = 'l2',
                             min_df = 1,
                             max_df = 0.25,
                             stop_words = 'english',
                             ngram_range = (1, 3),
                             smooth_idf = False,
                             sublinear_tf = True)
doc_model = vectorizer.fit_transform(corpus)

"""     This takes too long... need to try a different stemmer.
class StemmedTfidfVectorizer(TfidfVectorizer):
    def build_analyzer(self):
        stemmer = nltk.stem.SnowballStemmer('english')
        analyzer = super(TfidfVectorizer, self).build_analyzer()
        return lambda doc: (stemmer.stem(w) for w in analyzer(doc))

vectorizer = StemmedTfidfVectorizer(input = 'content',
                                    norm = 'l2',
                                    min_df = 1,
                                    max_df = 0.25,
                                    stop_words = 'english',
                                    ngram_range = (1, 3),
                                    smooth_idf = False,
                                    sublinear_tf = True)

"""

doc_score = doc_model.sum(axis=1).ravel().tolist()[0]
doc_rank = sorted(range(len(doc_score)), key=lambda k: doc_score[k], reverse=True)

topNum = 3
summaries = []
keywords = []

def get_summary(s_tokens,model,topNum):
    s_scores = zip(s_tokens,np.asarray(model.sum(axis=1)).ravel(),range(len(s_tokens)))
    sorted_s_scores = sorted(s_scores, key=lambda x: x[1], reverse=True)
    return sorted(sorted_s_scores[:topNum], key=lambda x: x[2])

def get_keywords(vectorizer,model,topNum):
    w_scores = zip(vectorizer.get_feature_names(),np.asarray(model.sum(axis=0)).ravel())
    sorted_w_scores = sorted(w_scores, key=lambda x: x[1], reverse=True)
    return sorted_w_scores[:topNum]

# make sure the vectorizer is taking raw content
vectorizer.input = 'content'

# go over each document
for article in corpus:
    # tokenize
    w_tokens = nltk.word_tokenize(article)
    s_tokens = nltk.sent_tokenize(article)
    # transform
    ss_model = vectorizer.transform(s_tokens)
    # analyze
    summary = get_summary(s_tokens,ss_model,topNum)
    keyword = get_keywords(vectorizer,ss_model,topNum)

    summaries.append(summary)
    keywords.append(keyword)

# today's keywords
t_keywords = get_keywords(vectorizer,doc_model,10)

#---------------------------------------------------------------------------------------------------
#                   Summarizing                                 ends
#---------------------------------------------------------------------------------------------------

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
	sources = {'name': 'CNBC and Seeking Alpha',
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
