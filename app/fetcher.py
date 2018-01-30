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

def get_summary(s_tokens,model,topNum):
    s_scores = zip(s_tokens,np.asarray(model.sum(axis=1)).ravel(),range(len(s_tokens)))
    sorted_s_scores = sorted(s_scores, key=lambda x: x[1], reverse=True)
    return sorted(sorted_s_scores[:topNum], key=lambda x: x[2])

def get_keywords(vectorizer,model,topNum):
    w_scores = zip(vectorizer.get_feature_names(),np.asarray(model.sum(axis=0)).ravel())
    sorted_w_scores = sorted(w_scores, key=lambda x: x[1], reverse=True)
    return sorted_w_scores[:topNum]

#---------------------------------------------------------------------------------------------------
#                   Scraping                                    begins
#---------------------------------------------------------------------------------------------------
def scrape():
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
    return corpus,header,source

#---------------------------------------------------------------------------------------------------
#                   Scraping                                    ends
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#                   Summarizing                                 begins
#---------------------------------------------------------------------------------------------------
def summarize():
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
    return vectorizer,doc_model,doc_score,doc_rank,summaries,keywords,t_keywords

#---------------------------------------------------------------------------------------------------
#                   Summarizing                                 ends
#---------------------------------------------------------------------------------------------------
