from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField
from wtforms import (
    StringField, PasswordField, TextAreaField, FloatField, SelectField,
    SubmitField, BooleanField, HiddenField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError, Optional

from app.models import User, Role


PROPERTY_TYPES = [
    ("apartment", "Apartment"),
    ("house", "House"),
    ("condo", "Condo"),
    ("townhouse", "Townhouse"),
    ("land", "Land"),
    ("commercial", "Commercial"),
]


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 64)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField(
        "Account type",
        choices=[(Role.USER, "Buyer / Renter"), (Role.OWNER, "Property Owner")],
        validators=[DataRequired()],
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Email already registered.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class IdentityVerificationForm(FlaskForm):
    document = FileField(
        "ID document (PNG, JPG, or PDF)",
        validators=[FileRequired(), FileAllowed(["png", "jpg", "jpeg", "pdf"], "Invalid file type.")],
    )
    submit = SubmitField("Submit for review")


class PropertyForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10)])
    price = FloatField("Price (USD)", validators=[DataRequired(), NumberRange(min=0)])
    location = StringField("Location", validators=[DataRequired(), Length(max=150)])
    property_type = SelectField("Property type", choices=PROPERTY_TYPES, validators=[DataRequired()])
    images = MultipleFileField(
        "Images (PNG/JPG/WEBP)",
        validators=[FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Images only.")],
    )
    submit = SubmitField("Save property")


class PropertyVerificationForm(FlaskForm):
    document = FileField(
        "Ownership document (PNG, JPG, or PDF)",
        validators=[FileRequired(), FileAllowed(["png", "jpg", "jpeg", "pdf"], "Invalid file type.")],
    )
    submit = SubmitField("Submit for review")


class ReviewForm(FlaskForm):
    decision = HiddenField(validators=[DataRequired()])
    note = TextAreaField("Note (optional)", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Submit decision")


class MessageForm(FlaskForm):
    subject = StringField("Subject", validators=[DataRequired(), Length(max=150)])
    body = TextAreaField("Message", validators=[DataRequired(), Length(min=2, max=2000)])
    submit = SubmitField("Send inquiry")


class SearchForm(FlaskForm):
    class Meta:
        csrf = False

    location = StringField("Location", validators=[Optional()])
    property_type = SelectField(
        "Type",
        choices=[("", "Any type")] + PROPERTY_TYPES,
        validators=[Optional()],
    )
    min_price = FloatField("Min price", validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField("Max price", validators=[Optional(), NumberRange(min=0)])
    verified_only = BooleanField("Verified only")
    submit = SubmitField("Search")
