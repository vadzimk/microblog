from datetime import datetime

from flask import render_template, flash, redirect, url_for, session

from .forms import LoginForm
from . import main


@main.route('/')
@main.route('/index')
def index():
    user = {'username': 'Miguel'}
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
    return render_template("index.html", title="Home", user=user, posts=posts, current_time=datetime.utcnow())


# dynamic route using <name>
@main.route('/hello/<name>')
def greet(name):
    return f'bYE there {name}'


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.username.data  # session is stored in client side cookie
        flash(f'login requested for user {form.username.data} {form.remember_me.data}')
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign in', form=form, username=session.get('username'))
