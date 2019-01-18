from flask import render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, validators
from itsdangerous import URLSafeTimedSerializer
import bcrypt

import functools
import urllib
import json
import datetime

import numpy as np
import re

from app import app

#---------------------------------------------------------------------------------------------------
#                   Settings                                    begins
#---------------------------------------------------------------------------------------------------
app.secret_key = "not much of a secret unless you let the cat run: ehwruigobrc2pn1   c0 y"
articles_per_source = 6
topNum = 3

app.config['MONGO_URI'] = 'mongodb://xibot:jacqep-4fubJy-ruhcoq@ds255784.mlab.com:55784/xinit'
mongo = PyMongo(app)
#---------------------------------------------------------------------------------------------------
#                   Settings                                    ends
#---------------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------
#                   Build for front end
#---------------------------------------------------------------------------------------------------


# iframe # this is a defaut iframe dict
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
      # {
      #    "symbols":iframe_news_symbols,
      #    "title":"News"
      # },
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

#---------------------------------------------------------------------------------------------------
#                   refreshing & threading
#---------------------------------------------------------------------------------------------------

# import threading
#
# import time
# import datetime
# from slackclient import SlackClient
#
# BOT_NAME = 'xibot'
# BOT_ID = 'U7MC33TL1'
# WEBSOCKET_DELAY = 10
# slack_client = SlackClient("-----------------------------------------------")
#
# def xibot():
#     if slack_client.rtm_connect():
#         print("StarterBot connected and running!")
#         while True:
#             response = """
#             <h1>Hello from heroku</h1>
#             <img src="http://loremflickr.com/600/400" />
#             """
#
#             slack_client.api_call("chat.postMessage", channel='xinit',
#                               text=response, as_user=True)
#             time.sleep(WEBSOCKET_DELAY)
#
# t = threading.Thread(target=xibot)
# #t.start()

#---------------------------------------------------------------------------------------------------
#                   Forms
#---------------------------------------------------------------------------------------------------

class LoginForm(FlaskForm):
    username = StringField('Username',
        [validators.DataRequired()],
        render_kw={"placeholder": "Username"})
    password = PasswordField('Password',
        [validators.DataRequired()],
        render_kw={"placeholder": "Password"})
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        login_user = mongo.db.users.find_one({'username' : self.username.data})
        if login_user:
            if bcrypt.hashpw(self.password.data.encode('utf-8'), login_user['password']) == login_user['password']:
                return True
        self.password.errors.append('Invalid username/password combination')
        return False

class RgstrForm(FlaskForm):
    username = StringField('Username',
        [validators.DataRequired(), validators.Length(min=4, max=25)],
        render_kw={"placeholder": "Username"})
    email = StringField('Email',
        [validators.DataRequired(), validators.Email(message='Invalid email format')],
        render_kw={"placeholder": "Email"})
    password = PasswordField('Password',
        [validators.DataRequired(),
         validators.Length(min=6),
         validators.EqualTo('confirm', message='Passwords must match')],
        render_kw={"placeholder": "Password"})
    confirm = PasswordField('Confirm Password',
        render_kw={"placeholder": "Confirm Password"})
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        existing_user = mongo.db.users.find_one({'username' : self.username.data})
        if existing_user is not None:
            self.username.errors.append('Username is already taken')
            return False
        existing_email = mongo.db.users.find_one({'email' : self.email.data})
        if existing_email is not None:
            self.email.errors.append('Email is already used')
            return False
        return True

class NewPostForm(FlaskForm):
    title = StringField('Title',
        [validators.DataRequired(), validators.Length(min=3)],
        render_kw={"placeholder": "Title"})
    abstract = TextAreaField('Abstract',
        [validators.DataRequired()],
        render_kw={"placeholder": "Abstract", "id": "summernote_abs"})
    content = TextAreaField('Content',
        [validators.DataRequired()],
        render_kw={"placeholder": "Content", "id": "summernote_ctt"})
    keywords = StringField('Keywords',
        render_kw={"placeholder": "Keywords separated by commas"})
    key_assets = StringField('Key Assets',
        render_kw={"placeholder": "Key assets separated by commas"})
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        return True

#---------------------------------------------------------------------------------------------------
#                   Web
#---------------------------------------------------------------------------------------------------

def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('username'):
            return fn(*args, **kwargs)
        return redirect(url_for('sign_in'))
    return inner


@app.route('/index')
def index():
    #if 'username' in session: # load user specific info

    page_data = mongo.db.processed_feeds.find_one()

    corpus = page_data['corpus']
    t_keywords = page_data['t_keywords']
    key_assets = page_data['key_assets']

    header = page_data['header']
    summaries = page_data['summaries']
    keywords = page_data['keywords']
    post_key_assets = page_data['post_key_assets']
    doc_score = page_data['doc_score']
    doc_rank = page_data['doc_rank']
    iframe_dict = page_data['iframe_dict']

    sources = {'name': 'news pieces', # 'CNBC, Bloomberg View, and Seeking Alpha',
               'length': len(corpus),
               'keywords': " || ".join([x[0] for x in t_keywords]),
               'key_assets': " || ".join([x for x in key_assets])}
    posts = [{'title': header[i][0],
              'content': "<br /><br />".join([x[0].replace('\n',' ') for x in summaries[i]]),
              'keywords': " || ".join([x[0] for x in keywords[i]]),
              'key_assets': " || ".join([x for x in post_key_assets[i]]),
              'condense_rate': "{:.3%}".format(sum([len(x[0]) for x in summaries[i]])/len(corpus[i])),
              'source': header[i][2],
              'score': "{:.3f}".format(doc_score[i]),
              'link': header[i][1]} for i in doc_rank]
    iframe_src = {'tv' : "https://s.tradingview.com/marketoverviewwidgetembed/#"
                         +urllib.parse.quote(str(json.dumps(iframe_dict)))}

    return render_template("index.html",
                           title='News',
                           sources=sources,
                           posts=posts,
                           iframe_src=iframe_src)

@app.route('/')
@app.route('/analyses')
def analyses():
    #if 'username' in session: # load user specific info

    posts = mongo.db.posts.find().limit(5);

    # make this iframe respond to analyses' assets -> used a different iframe dict
    iframe_src = {'tv' : "https://s.tradingview.com/marketoverviewwidgetembed/#"
                         +urllib.parse.quote(str(json.dumps(iframe_dict)))}

    return render_template("analyses.html",
                           title='Analyses',
                           posts=posts,
                           iframe_src=iframe_src)


@app.route('/new_post', methods=['POST', 'GET'])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        mongo.db.posts.insert({'title' : request.form['title'],
                               'abstract' : request.form['abstract'],
                               'content' : request.form['content'],
                               'keywords' : request.form['keywords'], # (semi)automate this
                               'key_assets' : request.form['key_assets'], # (semi)automate this
                               'time_added' : datetime.datetime.utcnow(),
                               'author' : session['username']})
        return redirect(url_for('analyses'))
    return render_template('new_post.html', form=form)

@app.route('/<string:id>/update_post', methods=['POST', 'GET'])
@login_required
def update_post(id):
    post = mongo.db.posts.find_one({'_id': ObjectId(id)})
    form = NewPostForm(data=post)
    if form.validate_on_submit():
        mongo.db.posts.update_one({'_id': ObjectId(id)},
            {'$set': {'title' : request.form['title'],
                      'abstract' : request.form['abstract'],
                      'content' : request.form['content'],
                      'keywords' : request.form['keywords'],
                      'key_assets' : request.form['key_assets']}
            })
        return redirect(url_for('analyses'))
    return render_template('new_post.html', form=form)


@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('sign_in.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RgstrForm()
    if form.validate_on_submit():
        hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        mongo.db.users.insert({'username' : request.form['username'],
                               'password' : hashpass,
                               'email' : request.form['email']})
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/profile') # make this username related maybe
@login_required
def user_profile():
    return render_template('profile.html')


@app.route('/sign_out', methods=['POST'])
def logout():
    # also log out of any databases or services
    session.clear()
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
