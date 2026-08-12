from flask import Blueprint, render_template, request
from sqlalchemy import or_

from app import db
from app.models import Property, Status
from app.forms import SearchForm

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    form = SearchForm(request.args, meta={"csrf": False})
    query = Property.query.filter(Property.listing_status == Status.APPROVED)

    location = request.args.get("location", "").strip()
    if location:
        query = query.filter(Property.location.ilike(f"%{location}%"))

    property_type = request.args.get("property_type", "").strip()
    if property_type:
        query = query.filter(Property.property_type == property_type)

    min_price = request.args.get("min_price", type=float)
    if min_price is not None:
        query = query.filter(Property.price >= min_price)

    max_price = request.args.get("max_price", type=float)
    if max_price is not None:
        query = query.filter(Property.price <= max_price)

    verified_only = request.args.get("verified_only") in ("y", "true", "on", "1")
    if verified_only:
        query = query.filter(Property.property_verification_status == Status.APPROVED)

    properties = query.order_by(Property.created_at.desc()).all()

    if verified_only:
        properties = [p for p in properties if p.is_fully_verified]

    return render_template(
        "index.html",
        properties=properties,
        form=form,
        verified_only=verified_only,
    )
