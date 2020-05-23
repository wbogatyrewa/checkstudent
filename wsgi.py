from app import app

from flask import Flask

server = Flask(__name__)
app = app.server


@app.route("/")
def home():
    return render_template("app.py")
