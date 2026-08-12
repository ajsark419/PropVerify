import secrets
from flask import url_for, current_app


def generate_token():
    return secrets.token_urlsafe(32)


def send_verification_email(user, token):
    """Mock email sender — prints a verification link to the console."""
    try:
        link = url_for("auth.verify_email", token=token, _external=True)
    except RuntimeError:
        link = f"/auth/verify-email?token={token}"
    current_app.logger.info("=" * 70)
    current_app.logger.info(f"[MOCK EMAIL] To: {user.email}")
    current_app.logger.info(f"[MOCK EMAIL] Subject: Verify your email")
    current_app.logger.info(f"[MOCK EMAIL] Link: {link}")
    current_app.logger.info("=" * 70)
    print("=" * 70)
    print(f"[MOCK EMAIL] To: {user.email}")
    print(f"[MOCK EMAIL] Click to verify: {link}")
    print("=" * 70)
