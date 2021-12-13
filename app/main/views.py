from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, logout_user, login_required
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User
from ..decorators import admin_required, permission_required
from ..models import Permission


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


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators"


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "For comment moderators"


@main.route('/user/<username>')
@login_required
def user(username):
    # when username does not exist 404 exception will be raised
    user = User.query.filter_by(username=username).first_or_404()
    # fake list of posts for this user
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.location.data = current_user.location
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.username.data
        user.role = form.role.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location
    form.about_me.date = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
