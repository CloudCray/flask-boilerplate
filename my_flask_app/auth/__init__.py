from flask import Blueprint
from flask_login import current_user
from flask import redirect, url_for

bp_auth = Blueprint('auth', __name__, url_prefix="/auth")

from . import views
from .models import User
from .. import login


@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()
