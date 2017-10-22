from flask import render_template
from app import app

import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import feedparser
import urllib
from bs4 import BeautifulSoup
import json

feed_url = 'https://www.cnbc.com/id/10000664/device/rss/rss.html'
d = feedparser.parse(feed_url)

@app.route('/')
@app.route('/index')
def index():
	return """hello"""
