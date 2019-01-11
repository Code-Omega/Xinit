#!flask/bin/python
from app import app
if __name__ == '__main__': #if __name__ == '_main_':
    app.run(debug=True, use_reloader=True)
