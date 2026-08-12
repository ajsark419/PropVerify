from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db


class Role:
    ADMIN = "admin"
    OWNER = "owner"
    USER = "user"
    ALL = (ADMIN, OWNER, USER)


class Status:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationKind:
    IDENTITY = "identity"
    PROPERTY = "property"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.USER)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(64), nullable=True)
    identity_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    properties = db.relationship("Property", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    verifications = db.relationship("Verification", backref="user", lazy="dynamic", cascade="all, delete-orphan", foreign_keys="Verification.user_id")
    sent_messages = db.relationship("Message", backref="sender", lazy="dynamic", foreign_keys="Message.sender_id")
    received_messages = db.relationship("Message", backref="recipient", lazy="dynamic", foreign_keys="Message.recipient_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_owner(self):
        return self.role in (Role.OWNER, Role.ADMIN)

    def latest_identity_verification(self):
        return (
            self.verifications.filter_by(kind=VerificationKind.IDENTITY)
            .order_by(Verification.created_at.desc())
            .first()
        )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(150), nullable=False, index=True)
    property_type = db.Column(db.String(50), nullable=False, index=True)
    listing_status = db.Column(db.String(20), nullable=False, default=Status.PENDING)
    property_verification_status = db.Column(db.String(20), nullable=False, default=Status.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = db.relationship("PropertyImage", backref="property", lazy="select", cascade="all, delete-orphan")
    verifications = db.relationship("Verification", backref="property", lazy="dynamic", cascade="all, delete-orphan", foreign_keys="Verification.property_id")
    messages = db.relationship("Message", backref="property", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_publicly_visible(self):
        return self.listing_status == Status.APPROVED

    @property
    def is_fully_verified(self):
        return (
            self.listing_status == Status.APPROVED
            and self.property_verification_status == Status.APPROVED
            and self.owner.identity_verified
        )

    def primary_image(self):
        return self.images[0] if self.images else None


class PropertyImage(db.Model):
    __tablename__ = "property_images"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Verification(db.Model):
    __tablename__ = "verifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=True)
    kind = db.Column(db.String(20), nullable=False)
    document_filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=Status.PENDING)
    admin_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    reviewed_by = db.relationship("User", foreign_keys=[reviewed_by_id])


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=True)
    subject = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
