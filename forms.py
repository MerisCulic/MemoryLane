from models import db, User
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask import request


class RegistrationForm(FlaskForm):

    firstname = StringField('First name', validators=[DataRequired()])
    surname = StringField('Surname')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    confirm_password = PasswordField('Confirm-password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_email(self, email):
        user = db.query(User).filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email address is already taken! Please enter a different one.')

class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):

    firstname = StringField('First name', validators=[DataRequired()])
    surname = StringField('Surname')
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['png', 'jpg'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()
        if email.data != user.email:
            user = db.query(User).filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email address is already taken! Please enter a different one.')