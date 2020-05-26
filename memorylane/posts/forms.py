from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Title', render_kw={"placeholder": "You can add a post title here."})
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"placeholder": "Want to share something with the others?"})
    submit = SubmitField('Share')


class PostEditForm(FlaskForm):
    title = StringField('Title', render_kw={"placeholder": "You can add a post title here."})
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 6})
    submit = SubmitField('Update')
