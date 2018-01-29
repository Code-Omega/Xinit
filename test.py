from flask import Flask
first_app = Flask(__name__)

@first_app.route("/")
def first_function():
    return "<html><body><h1 style='color:red'>I am hosted on Raspberry Pi !!!</h1></body></html>"

if __name__ == "__main__":
    first_app.run(host='0.0.0.0')