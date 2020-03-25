from sqla_wrapper import SQLAlchemy
import os


db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite?check_same_thread=False")) #TODO: Change localhost to heroku

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    session_token = db.Column(db.String)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String)
    sender_name = db.Column(db.String)
    reciever = db.Column(db.String)
    title = db.Column(db.String)
    date_posted = db.Column(db.DateTime)
    message_text = db.Column(db.Text)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

