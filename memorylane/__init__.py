from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xbf,\x92\xda\x11\x844\xae\xf4i\xd36\x01\xef\xb4'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///localhost.sqlite?check_same_thread=False" #TODO: Change localhost to heroku
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = 'You need to be logged in to view that page!'
login_manager.login_message_category = 'info'

from memorylane import routes