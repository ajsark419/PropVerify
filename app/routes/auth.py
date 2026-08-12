from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse

from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from app.services.email_service import generate_token, send_verification_email

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            role=form.role.data,
        )
        user.set_password(form.password.data)
        token = generate_token()
        user.email_verification_token = token
        db.session.add(user)
        db.session.commit()
        send_verification_email(user, token)
        flash("Account created. Check the server console for the email verification link.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember.data)
        flash(f"Welcome back, {user.username}!", "success")
        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@bp.route("/verify-email")
def verify_email():
    token = request.args.get("token", "")
    if not token:
        flash("Missing verification token.", "danger")
        return redirect(url_for("main.index"))
    user = User.query.filter_by(email_verification_token=token).first()
    if user is None:
        flash("Invalid or expired verification link.", "danger")
        return redirect(url_for("main.index"))
    user.email_verified = True
    user.email_verification_token = None
    db.session.commit()
    flash("Email verified. You can now sign in.", "success")
    return redirect(url_for("auth.login"))


@bp.route("/resend-verification")
@login_required
def resend_verification():
    if current_user.email_verified:
        flash("Your email is already verified.", "info")
        return redirect(url_for("main.index"))
    token = generate_token()
    current_user.email_verification_token = token
    db.session.commit()
    send_verification_email(current_user, token)
    flash("Verification link sent. Check the server console.", "success")
    return redirect(url_for("main.index"))
