from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from bookbits.config import Config


mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = 'You need to be logged in to view that page!'
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from bookbits.users.routes import users
    from bookbits.posts.routes import posts
    from bookbits.messages.routes import messages
    from bookbits.main.routes import main
    from bookbits.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(messages)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
