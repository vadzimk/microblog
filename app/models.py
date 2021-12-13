import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from hashlib import md5


# after each modification in models.py
# need to run two commands:
# flask db migrate
# flask db upgrade

# tell flask-login how to load user from db
@login.user_loader
def load_user(id):
    return User.query.get(int(id))  # converts string to int for the db


# UserMixin that includes generic implementations of required fields for loginManager
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    confirmed = db.Column(db.Boolean, default=False)  # account email confirmed
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(140))
    avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        """ write only property """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # generate a token
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    # verifies token
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True  # sets db column value
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    # gravatar service will be blcked boy ghostery because it allows it to collect data on which sites you visited.
    def gravatar(self, size, default='identicon', rating='g'):
        """ :return url of user avatar image scaled to the size in pixels"""
        # encode --> bytes
        # hexdigest --> hash string in hexidecimal

        url='https://secure.gravatar.com/avatar'
        digest = self.avatar_hash or self.gravatar_hash()
        return f'{url}/{digest}?d={default}&s={size}&r={rating}'

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # default role is assigned to each new user
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    user = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f'<Role> {self.name}'

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        # new roles can be updated in the future
        # anonymous role does not need to be represented
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = role.name == default_role
            db.session.add(role)
        db.session.commit()


class Permission:
    # powers of 2 allow to have unique combinations by summing up individual permissions
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16
