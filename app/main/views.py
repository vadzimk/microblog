from datetime import datetime

from flask import render_template, flash, redirect, url_for
from flask_login import current_user, logout_user, login_required
from .forms import RegistrationForm
from . import main
from .. import db
from ..models import User


@main.route('/')
@main.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html", title="Home", posts=posts, current_time=datetime.utcnow())


# dynamic route using <name>
@main.route('/hello/<name>')
@login_required
def greet(name):
    return f'bYE there {name}'







@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash(f'Congratulations {form.username.data} you are now registered user')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

