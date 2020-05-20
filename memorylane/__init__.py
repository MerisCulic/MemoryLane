from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xbf,\x92\xda\x11\x844\xae\xf4i\xd36\x01\xef\xb4'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///localhost.sqlite?check_same_thread=False" #TODO: Change localhost to heroku
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from memorylane import routes