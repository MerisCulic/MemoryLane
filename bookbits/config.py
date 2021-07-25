import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DB_URI', "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'  # TODO: Change mail server value if ML acc not on gmail
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')  # TODO: Create ML e-mail acc and change env vars in os
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')

