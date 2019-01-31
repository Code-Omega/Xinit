from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

from flask import Flask
from flask_pymongo import PyMongo

import ana

############################ SAMPLE SCHEDULES ############################
# @sched.scheduled_job('interval', minutes=3)
# def timed_job():
#     print('This job is run every three minutes.')
#
# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')
##########################################################################

@sched.scheduled_job('interval', minutes=1)
def process_feeds(): # separate into another job for getting feed
    print('Process feeds, runs every 30 minutes.')

    # SETTINGS

    app = Flask(__name__)
    app.config['MONGO_URI'] = 'mongodb://xibot:jacqep-4fubJy-ruhcoq@ds255784.mlab.com:55784/xinit'
    mongo = PyMongo(app)

    # CALL FUNCTION
    res = ana.processed_feeds(articles_per_source = 6,
                              topNum = 3)

    # STORE RESULTS
    iframe_tab = {"symbols":res.iframe_news_symbols,"title":"News"}
    mongo.db.processed_feeds.drop()
    mongo.db.processed_feeds.insert(
        {'corpus' : res.corpus,
         't_keywords' : res.t_keywords,
         'key_assets' : res.key_assets,
         'header' : res.header,
         'summaries' : res.summaries,
         'keywords' : res.keywords,
         'post_key_assets' : res.post_key_assets,
         'doc_score' : res.doc_score,
         'doc_rank' : res.doc_rank,
         'iframe_tab' : iframe_tab,
         })


@sched.scheduled_job('interval', minutes=30)
def cache_daily_data():
    print('get daily minute level data (snp), runs every 30 minutes in testing phase.')


# @sched.scheduled_job('interval', minutes=30)
# def daily_clustering_analysis():
#     print('Daily clustering analysis, runs every 30 minutes in testing phase.')



sched.start()
