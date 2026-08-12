from functools import wraps
from flask import abort
from flask_login import current_user

from app.models import Role


def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(func):
    return role_required(Role.ADMIN)(func)


def owner_required(func):
    return role_required(Role.OWNER, Role.ADMIN)(func)
