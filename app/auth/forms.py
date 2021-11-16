from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email
from wtforms import StringField, BooleanField, SubmitField, PasswordField


class LoginForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')  # checkbox
    submit = SubmitField('Sign in')