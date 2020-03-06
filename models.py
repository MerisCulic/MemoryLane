from sqla_wrapper import SQLAlchemy
import os

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    session_token = db.Column(db.String)


class Sent_messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String)
    reciever = db.Column(db.String)
    title = db.Column(db.String)
    message_text = db.Column(db.String)

class Recieved_messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String)
    title = db.Column(db.String)
    message_text = db.Column(db.String)