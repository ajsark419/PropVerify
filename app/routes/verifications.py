from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models import Verification, VerificationKind, Status
from app.forms import IdentityVerificationForm
from app.services.file_service import save_document

bp = Blueprint("verifications", __name__)


@bp.route("/identity", methods=["GET", "POST"])
@login_required
def identity():
    latest = current_user.latest_identity_verification()
    form = IdentityVerificationForm()
    if form.validate_on_submit():
        try:
            rel = save_document(form.document.data, "ids")
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(request.url)
        v = Verification(
            user_id=current_user.id,
            kind=VerificationKind.IDENTITY,
            document_filename=rel,
            status=Status.PENDING,
        )
        db.session.add(v)
        db.session.commit()
        flash("Identity document submitted for admin review.", "success")
        return redirect(url_for("verifications.identity"))

    return render_template("verifications/identity.html", form=form, latest=latest)
