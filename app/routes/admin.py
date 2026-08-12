from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from app import db
from app.models import User, Property, Verification, VerificationKind, Status, Role
from app.decorators import admin_required

bp = Blueprint("admin", __name__)


@bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "users": User.query.count(),
        "properties": Property.query.count(),
        "pending_identity": Verification.query.filter_by(kind=VerificationKind.IDENTITY, status=Status.PENDING).count(),
        "pending_property": Verification.query.filter_by(kind=VerificationKind.PROPERTY, status=Status.PENDING).count(),
        "pending_listings": Property.query.filter_by(listing_status=Status.PENDING).count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@bp.route("/users/<int:user_id>/toggle-role", methods=["POST"])
@login_required
@admin_required
def toggle_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own role.", "warning")
        return redirect(url_for("admin.users"))
    if user.role == Role.USER:
        user.role = Role.OWNER
    elif user.role == Role.OWNER:
        user.role = Role.USER
    db.session.commit()
    flash(f"{user.username} role updated to {user.role}.", "success")
    return redirect(url_for("admin.users"))


@bp.route("/verifications/identity")
@login_required
@admin_required
def identity_queue():
    pending = (
        Verification.query.filter_by(kind=VerificationKind.IDENTITY)
        .order_by(Verification.created_at.desc())
        .all()
    )
    return render_template("admin/identity_queue.html", verifications=pending)


@bp.route("/verifications/property")
@login_required
@admin_required
def property_queue():
    pending = (
        Verification.query.filter_by(kind=VerificationKind.PROPERTY)
        .order_by(Verification.created_at.desc())
        .all()
    )
    return render_template("admin/property_queue.html", verifications=pending)


@bp.route("/verifications/<int:verification_id>/decide", methods=["POST"])
@login_required
@admin_required
def decide_verification(verification_id):
    v = Verification.query.get_or_404(verification_id)
    decision = request.form.get("decision")
    note = request.form.get("note", "").strip() or None
    if decision not in (Status.APPROVED, Status.REJECTED):
        flash("Invalid decision.", "danger")
        return redirect(request.referrer or url_for("admin.dashboard"))

    v.status = decision
    v.admin_note = note
    v.reviewed_at = datetime.utcnow()
    v.reviewed_by_id = current_user.id

    if v.kind == VerificationKind.IDENTITY:
        v.user.identity_verified = (decision == Status.APPROVED)
    elif v.kind == VerificationKind.PROPERTY and v.property is not None:
        v.property.property_verification_status = decision

    db.session.commit()
    flash(f"Verification {decision}.", "success")
    return redirect(request.referrer or url_for("admin.dashboard"))


@bp.route("/listings")
@login_required
@admin_required
def listings_queue():
    pending = Property.query.filter_by(listing_status=Status.PENDING).order_by(Property.created_at.desc()).all()
    other = Property.query.filter(Property.listing_status != Status.PENDING).order_by(Property.created_at.desc()).all()
    return render_template("admin/listings.html", pending=pending, other=other)


@bp.route("/listings/<int:property_id>/decide", methods=["POST"])
@login_required
@admin_required
def decide_listing(property_id):
    prop = Property.query.get_or_404(property_id)
    decision = request.form.get("decision")
    if decision not in (Status.APPROVED, Status.REJECTED):
        flash("Invalid decision.", "danger")
        return redirect(url_for("admin.listings_queue"))
    prop.listing_status = decision
    db.session.commit()
    flash(f"Listing #{prop.id} {decision}.", "success")
    return redirect(url_for("admin.listings_queue"))
