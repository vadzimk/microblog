from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, BooleanField, SubmitField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')