from memorylane.models import User
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user


class RegistrationForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired()])
    surname = StringField('Surname')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    confirm_password = PasswordField('Confirm-password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email address is already taken! Please enter a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired()])
    surname = StringField('Surname')
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['png', 'jpg'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email address is already taken! Please enter a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', render_kw={"placeholder": "You can add a post title here."})
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"placeholder": "Want to share something with the others?"})
    submit = SubmitField('Share')


class PostEditForm(FlaskForm):
    title = StringField('Title', render_kw={"placeholder": "You can add a post title here."})
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 6})
    submit = SubmitField('Update')