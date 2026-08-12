import os
from flask import Blueprint, send_from_directory, abort, current_app
from flask_login import login_required, current_user

from app.models import Role

bp = Blueprint("uploads", __name__)


@bp.route("/properties/<path:filename>")
def property_image(filename):
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "properties")
    if not os.path.isfile(os.path.join(folder, filename)):
        abort(404)
    return send_from_directory(folder, filename)


@bp.route("/ids/<path:filename>")
@login_required
def id_document(filename):
    if current_user.role != Role.ADMIN:
        abort(403)
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "ids")
    if not os.path.isfile(os.path.join(folder, filename)):
        abort(404)
    return send_from_directory(folder, filename)


@bp.route("/ownership/<path:filename>")
@login_required
def ownership_document(filename):
    if current_user.role != Role.ADMIN:
        abort(403)
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "ownership")
    if not os.path.isfile(os.path.join(folder, filename)):
        abort(404)
    return send_from_directory(folder, filename)
