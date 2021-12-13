from datetime import datetime

from . import auth
from flask_login import current_user, login_user
from .forms import LoginForm
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from ..models import User
from flask_login import current_user, logout_user, login_required
from .forms import RegistrationForm
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print('user', user)
        if user is None or not user.verify_password(form.password.data):
            flash(f'Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)

        # allows to remember where to redirect after successful login
        next_page = request.args.get('next')
        if not next_page or url_parse(
                next_page).netloc != '':  # https://stackoverflow.com/questions/53992694/what-does-netloc-mean
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign in', form=form)
    #     session['name'] = form.username.data  # session is stored in client side cookie
    #     flash(f'login requested for user {form.username.data} {form.remember_me.data}')
    #     return redirect(url_for('main.index'))
    # return render_template('login.html', title='Sign in', form=form, username=session.get('username'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()  # must be before confirmation is sent out
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your account', 'auth/email/confirm', user=user, token=token)
        flash(f'Congratulations {form.username.data} you are now registered user')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/confirm/<token>')  # token variable is created here
@login_required  # user is asked to login before they reach this view function
def confirm(token):  # token variable is consumed here
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed account. Thanks')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


# executed before each request for all blueprints even outside the blueprint
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


# before_request is executed before each request in this blueprint


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your account', 'auth/email/confirm', user=current_user, token=token)
    flash(f'A new confirmation email has been sent to {current_user.email}')
    return redirect(url_for('main.index'))
