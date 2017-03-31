import json

from flask import jsonify, request, abort, url_for, flash, render_template, redirect
from flask_admin.contrib import sqla
from flask_login import login_required, current_user, login_user, logout_user

from . import bp_auth
from .models import User, Role
from .forms import LoginForm, EmailForm, PasswordForm, RegistrationForm
from .decorators import token_permission_required

from .. import admin
from .. import db
from ..mail.models import EmailMessage


@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for("base.index"))
        flash("Invalid email or password")
    return render_template("auth/login.html", form=form)


@bp_auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out")
    return redirect(url_for("base.index"))


@bp_auth.route("/token", methods=["POST"])
def get_auth_token():
    if not request.json:
        abort(400)
    js = json.loads(request.json)
    api_key = js.get("api_key")
    if api_key:
        user = User.from_key(api_key)
        verified = True
    else:
        email = js.get("email")
        pwd = js.get("password")
        user = User.query.filter_by(email=email).first()
        verified = user.verify_password(pwd)

    if user is not None and verified:
        token = user.generate_auth_token()
        return jsonify({"token": token.decode("ascii")})
    else:
        return abort(403)


@bp_auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.password = form.password.data

        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()

        email_message = EmailMessage(subject="Confirm Your Account", recipients=[user.email])
        email_message.set_template("email/confirm", user=user, token=token)
        email_message.send()

        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@bp_auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('base.index'))
    if current_user.confirm(token):
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for('base.index'))


@bp_auth.route("/reset", methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()
        subject = "Password reset requested"
        token = user.generate_email_token()

        email_message = EmailMessage(subject=subject, recipients=[user.email])
        email_message.set_template("email/password-reset", token=token)
        email_message.send()

        return redirect(url_for('base.index'))
    return render_template('auth/reset.html', form=form)


@bp_auth.route("/reset/<token>", methods=["GET", "POST"])
def reset_with_token(token):
    try:
        user = User.verify_email_reset_token(token)
        form = PasswordForm()
        if form.validate_on_submit():
            user.password = form.password.data

            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))
        return render_template("auth/reset-with-token.html", form=form, token=token)
    except Exception as ex:
        abort(404)


# Create customized model view class
class AdminModelView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.can('administrator'):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('auth.login', next=request.url))


admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Role, db.session))