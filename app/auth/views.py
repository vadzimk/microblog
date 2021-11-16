from . import auth
from flask_login import current_user, login_user
from .forms import LoginForm
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from ..models import User
from flask_login import current_user, logout_user, login_required

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
        if not next_page or url_parse(next_page).netloc != '':  # https://stackoverflow.com/questions/53992694/what-does-netloc-mean
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