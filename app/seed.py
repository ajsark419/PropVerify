from flask import current_app
from app import db
from app.models import User, Role


def seed_default_admin():
    email = current_app.config["DEFAULT_ADMIN_EMAIL"]
    existing = User.query.filter_by(email=email).first()
    if existing:
        return existing
    admin = User(
        username=current_app.config["DEFAULT_ADMIN_USERNAME"],
        email=email,
        role=Role.ADMIN,
        email_verified=True,
        identity_verified=True,
    )
    admin.set_password(current_app.config["DEFAULT_ADMIN_PASSWORD"])
    db.session.add(admin)
    db.session.commit()
    print(f"[SEED] Created default admin: {email} / {current_app.config['DEFAULT_ADMIN_PASSWORD']}")
    return admin
