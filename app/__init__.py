# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

boostrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
login = LoginManager()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    boostrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login.init_app(app)
    login.login_view = 'main.login'  # function name for login view i.e. name used in url_for()
    # works with @login_required decorator below @app.route decorator from Flask

    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app


from app import models
