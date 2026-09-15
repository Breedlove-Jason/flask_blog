from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, URL, Email, Length

class CreatePostForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired(), Length(max=250)])
    subtitle = StringField('Subtitle', validators=[DataRequired(), Length(max=250)])
    img_url = StringField('Blog Image URL', validators=[DataRequired(), URL(), Length(max=250)])
    body = TextAreaField('Blog Content', validators=[DataRequired(), Length(max=100000)])
    submit = SubmitField('Publish post')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password (at least 12 characters)', validators=[DataRequired(), Length(min=12, max=128)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Log in')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(max=250)])
    submit_comment = SubmitField('Submit comment')
