import os
import secrets
from werkzeug.utils import secure_filename
from flask import current_app


def _allowed(filename, allowed_set):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_set


def save_document(file_storage, subfolder):
    if file_storage is None or not file_storage.filename:
        return None
    allowed = current_app.config["ALLOWED_DOC_EXTENSIONS"]
    if not _allowed(file_storage.filename, allowed):
        raise ValueError("File type not allowed.")
    return _save(file_storage, subfolder)


def save_image(file_storage, subfolder):
    if file_storage is None or not file_storage.filename:
        return None
    allowed = current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    if not _allowed(file_storage.filename, allowed):
        raise ValueError("Image type not allowed.")
    return _save(file_storage, subfolder)


def _save(file_storage, subfolder):
    base = current_app.config["UPLOAD_FOLDER"]
    folder = os.path.join(base, subfolder)
    os.makedirs(folder, exist_ok=True)
    safe = secure_filename(file_storage.filename)
    ext = safe.rsplit(".", 1)[1].lower() if "." in safe else "bin"
    new_name = f"{secrets.token_hex(16)}.{ext}"
    path = os.path.join(folder, new_name)
    file_storage.save(path)
    return f"{subfolder}/{new_name}"


def absolute_path(relative):
    return os.path.join(current_app.config["UPLOAD_FOLDER"], relative)
