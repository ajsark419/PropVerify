from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from app import db
from app.models import Property, PropertyImage, Status, Role
from app.forms import PropertyForm, PropertyVerificationForm, MessageForm
from app.services.file_service import save_image
from app.decorators import owner_required

bp = Blueprint("properties", __name__)


@bp.route("/mine")
@login_required
@owner_required
def mine():
    properties = current_user.properties.order_by(Property.created_at.desc()).all()
    return render_template("properties/mine.html", properties=properties)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@owner_required
def new():
    if not current_user.identity_verified:
        flash("You must complete identity verification before creating listings.", "warning")
        return redirect(url_for("verifications.identity"))

    form = PropertyForm()
    if form.validate_on_submit():
        prop = Property(
            owner_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            location=form.location.data,
            property_type=form.property_type.data,
            listing_status=Status.PENDING,
            property_verification_status=Status.PENDING,
        )
        db.session.add(prop)
        db.session.flush()

        for f in form.images.data or []:
            if f and f.filename:
                try:
                    rel = save_image(f, "properties")
                    if rel:
                        db.session.add(PropertyImage(property_id=prop.id, filename=rel))
                except ValueError as e:
                    flash(str(e), "danger")

        db.session.commit()
        flash("Listing created. Submit ownership documents and wait for admin approval.", "success")
        return redirect(url_for("properties.detail", property_id=prop.id))

    return render_template("properties/edit.html", form=form, property=None)


@bp.route("/<int:property_id>")
def detail(property_id):
    prop = Property.query.get_or_404(property_id)
    is_owner_or_admin = (
        current_user.is_authenticated
        and (current_user.id == prop.owner_id or current_user.role == Role.ADMIN)
    )
    if not prop.is_publicly_visible and not is_owner_or_admin:
        abort(404)

    message_form = MessageForm() if current_user.is_authenticated and current_user.id != prop.owner_id else None
    return render_template(
        "properties/detail.html",
        property=prop,
        message_form=message_form,
        is_owner_or_admin=is_owner_or_admin,
    )


@bp.route("/<int:property_id>/edit", methods=["GET", "POST"])
@login_required
def edit(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id and current_user.role != Role.ADMIN:
        abort(403)

    form = PropertyForm(obj=prop)
    if form.validate_on_submit():
        prop.title = form.title.data
        prop.description = form.description.data
        prop.price = form.price.data
        prop.location = form.location.data
        prop.property_type = form.property_type.data
        prop.listing_status = Status.PENDING

        for f in form.images.data or []:
            if f and f.filename:
                try:
                    rel = save_image(f, "properties")
                    if rel:
                        db.session.add(PropertyImage(property_id=prop.id, filename=rel))
                except ValueError as e:
                    flash(str(e), "danger")

        db.session.commit()
        flash("Listing updated and re-submitted for approval.", "success")
        return redirect(url_for("properties.detail", property_id=prop.id))

    return render_template("properties/edit.html", form=form, property=prop)


@bp.route("/<int:property_id>/delete", methods=["POST"])
@login_required
def delete(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id and current_user.role != Role.ADMIN:
        abort(403)
    db.session.delete(prop)
    db.session.commit()
    flash("Listing deleted.", "info")
    return redirect(url_for("properties.mine"))


@bp.route("/<int:property_id>/verify", methods=["GET", "POST"])
@login_required
def submit_property_verification(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id:
        abort(403)

    form = PropertyVerificationForm()
    if form.validate_on_submit():
        from app.services.file_service import save_document
        from app.models import Verification, VerificationKind
        try:
            rel = save_document(form.document.data, "ownership")
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(request.url)
        v = Verification(
            user_id=current_user.id,
            property_id=prop.id,
            kind=VerificationKind.PROPERTY,
            document_filename=rel,
            status=Status.PENDING,
        )
        prop.property_verification_status = Status.PENDING
        db.session.add(v)
        db.session.commit()
        flash("Ownership document submitted for review.", "success")
        return redirect(url_for("properties.detail", property_id=prop.id))

    return render_template("properties/verify.html", form=form, property=prop)
