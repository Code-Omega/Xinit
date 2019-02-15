from flask import Flask
from flask_pymongo import PyMongo

import ana

MONGO_URI = 'mongodb://xibot:jacqep-4fubJy-ruhcoq@ds255784.mlab.com:55784/xinit'

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URI
mongo = PyMongo(app)

print('Process with new feeds.')
ana.process_feeds(mongo, num_posts = 6, topNum = 3)
print('Feeds processed.')

# print('Updating trends.')
# ana.get_google_trends(mongo, 12)
# print('trends updated.')
