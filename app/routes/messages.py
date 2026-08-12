from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from app import db
from app.models import Message, Property
from app.forms import MessageForm

bp = Blueprint("messages", __name__)


@bp.route("/inbox")
@login_required
def inbox():
    received = (
        Message.query.filter_by(recipient_id=current_user.id)
        .order_by(Message.created_at.desc())
        .all()
    )
    sent = (
        Message.query.filter_by(sender_id=current_user.id)
        .order_by(Message.created_at.desc())
        .all()
    )
    return render_template("messages/inbox.html", received=received, sent=sent)


@bp.route("/<int:message_id>")
@login_required
def view(message_id):
    msg = Message.query.get_or_404(message_id)
    if msg.recipient_id != current_user.id and msg.sender_id != current_user.id:
        abort(403)
    if msg.recipient_id == current_user.id and not msg.read:
        msg.read = True
        db.session.commit()
    return render_template("messages/view.html", message=msg)


@bp.route("/inquire/<int:property_id>", methods=["POST"])
@login_required
def inquire(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id == current_user.id:
        flash("You cannot inquire about your own listing.", "warning")
        return redirect(url_for("properties.detail", property_id=prop.id))

    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(
            sender_id=current_user.id,
            recipient_id=prop.owner_id,
            property_id=prop.id,
            subject=form.subject.data,
            body=form.body.data,
        )
        db.session.add(msg)
        db.session.commit()
        flash("Inquiry sent to the owner.", "success")
    else:
        for field, errors in form.errors.items():
            for err in errors:
                flash(f"{field}: {err}", "danger")
    return redirect(url_for("properties.detail", property_id=prop.id))
