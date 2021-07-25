from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', render_kw={"placeholder": "You can add the book title here."})
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"placeholder": "Which little bit of a book got you thinking?"})
    submit = SubmitField('Share')


class PostEditForm(FlaskForm):
    title = StringField('Title', render_kw={"placeholder": "You can add the book title here."})
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 6})
    submit = SubmitField('Update')


class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"placeholder": " Add a comment.."})
    submit = SubmitField('Comment')


class CommentEditForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 6})
    submit = SubmitField('Update')