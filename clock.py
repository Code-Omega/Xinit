from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

from flask import Flask
from flask_pymongo import PyMongo

import ana

MONGO_URI = 'mongodb://xibot:jacqep-4fubJy-ruhcoq@ds255784.mlab.com:55784/xinit'

############################ SAMPLE SCHEDULES ############################
# @sched.scheduled_job('interval', minutes=3)
# def timed_job():
#     print('This job is run every three minutes.')
#
# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')
##########################################################################


@sched.scheduled_job('interval', minutes=30)
def process_feeds():
    print('Getting feed data; runs every 30 minutes.')
    app = Flask(__name__)
    app.config['MONGO_URI'] = MONGO_URI
    mongo = PyMongo(app)

    num_new_posts = ana.get_feeds(mongo)
    print('# new posts:',num_new_posts)
    if num_new_posts > 0:
        print('Process with new feeds.')
        ana.process_feeds(mongo, num_posts = 10, topNum = 3)
        print('Feeds processed')


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=20)
def retrain_doc_model():
    print('Retrain the tfidf model; runs every day at night.')
    ana.update_doc_model(mongo)
    print('Model retrained')


# @sched.scheduled_job('interval', minutes=30)
# def cache_daily_data():
#     print('get daily minute level data (snp), runs every 30 minutes in testing phase.')


# @sched.scheduled_job('interval', minutes=30)
# def daily_clustering_analysis():
#     print('Daily clustering analysis, runs every 30 minutes in testing phase.')



sched.start()
