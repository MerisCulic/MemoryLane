from sqla_wrapper import SQLAlchemy
import os


db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite?check_same_thread=False")) #TODO: Change localhost to heroku

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String)
    surname = db.Column(db.String)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    image_file = db.Column(db.String(20), default='default_avatar.jpg')
    session_token = db.Column(db.String)
    posts = db.relationship('Posts', backref='author', lazy=True)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String)
    sender_name = db.Column(db.String)
    reciever = db.Column(db.String)
    title = db.Column(db.String)
    date_posted = db.Column(db.DateTime)
    message_text = db.Column(db.Text)


class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


