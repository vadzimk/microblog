from datetime import datetime

from flask import render_template, flash, redirect, url_for, session, request
from flask_login import current_user, login_user, logout_user, login_required
from .forms import LoginForm, RegistrationForm
from . import main
from .. import db
from ..models import User
from werkzeug.urls import url_parse


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


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print('user', user)
        if user is None or not user.check_password(form.password.data):
            flash(f'Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)
    #     session['name'] = form.username.data  # session is stored in client side cookie
    #     flash(f'login requested for user {form.username.data} {form.remember_me.data}')
    #     return redirect(url_for('main.index'))
    # return render_template('login.html', title='Sign in', form=form, username=session.get('username'))


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Congratulations {form.username.data} you are now registered user')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

