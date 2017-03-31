import os

from flask import Flask
from .config import read_config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin

app = Flask(__name__)
db = SQLAlchemy()
login = LoginManager()
mail_manager = Mail()
admin = Admin(template_mode="bootstrap3")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app(config_name):
    app = Flask(__name__)

    db_config = read_config("database", config_name)
    flask_config = read_config("flask", config_name)

    db_driver = db_config["driver"]
    if db_driver == "sqlite":
        db_uri = '{0}:///./../{1}'.format(
            db_config["driver"],
            db_config["database"]
        )
    else:
        db_uri = '{0}://{1}:{2}@{3}/{4}'.format(
            db_config["driver"],
            db_config["user"],
            db_config["password"],
            db_config["server"],
            db_config["database"])

    app.config.update(
        ENVIRONMENT_NAME=config_name,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=flask_config["debug"],
        SECRET_KEY=flask_config["secret_key"],
        SQLALCHEMY_COMMIT_ON_TEARDOWN=flask_config["teardown_commit"],
        SQLALCHEMY_DATABASE_URI=db_uri,
    )

    db.init_app(app)
    login.init_app(app)
    mail_manager.init_app(app)
    admin.init_app(app)

    login.login_view = "auth.login"

    app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

    from .base import bp
    from .auth import bp_auth
    #  from .some_module import bp_some_module

    app.register_blueprint(bp)
    app.register_blueprint(bp_auth)
    #  app.register_blueprint(bp_some_module)

    return app


def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)
