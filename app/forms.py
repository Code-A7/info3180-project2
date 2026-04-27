"""
Forms module for the dating application.

This module contains all the Flask-WTF forms used in the application,
including registration, login, and profile forms.
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from app.models import User


class RegistrationForm(FlaskForm):
    """
    Form for user registration.

    Fields:
        email: User's email address
        password: User's password
        confirm_password: Password confirmation
    """

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Please enter a valid email address"),
            Length(
                min=6, max=120, message="Email must be between 6 and 120 characters"
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required"),
            Length(min=8, message="Password must be at least 8 characters"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password"),
            EqualTo("password", message="Passwords must match"),
        ],
    )

    def validate_email(self, email):
        """
        Validate that the email is not already registered.

        Args:
            email: The email field to validate

        Raises:
            ValidationError: If the email is already registered
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is already registered")


class LoginForm(FlaskForm):
    """
    Form for user login.

    Fields:
        email: User's email address
        password: User's password
    """

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Please enter a valid email address"),
        ],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Password is required")]
    )


class ProfileForm(FlaskForm):
    """
    Form for user profile creation and editing.

    Fields:
        name: User's name
        age: User's age
        bio: User's biography
        interests: User's interests (comma separated)
        gender: User's gender
        gender_preference: User's gender preference for matches
        relationship_goal: User's relationship goal
        occupation: User's occupation
        visibility: Whether profile is public
    """

    name = StringField(
        "Name",
        validators=[
            DataRequired(message="Name is required"),
            Length(min=2, max=100, message="Name must be between 2 and 100 characters"),
        ],
    )
    age = IntegerField(
        "Age",
        validators=[
            DataRequired(message="Age is required"),
            NumberRange(min=18, max=120, message="You must be at least 18 years old"),
        ],
    )
    bio = TextAreaField(
        "Bio",
        validators=[
            Optional(),
            Length(max=500, message="Bio must be less than 500 characters"),
        ],
    )
    interests = StringField(
        "Interests (comma separated)",
        validators=[
            DataRequired(message="Please add at least 3 interests"),
        ],
    )
    gender = SelectField(
        "Gender",
        choices=[
            ("", "Select Gender"),
            ("male", "Male"),
            ("female", "Female"),
            ("non_binary", "Non-Binary"),
            ("other", "Other"),
            ("prefer_not_to_say", "Prefer not to say"),
        ],
    )
    gender_preference = SelectField(
        "Interested In",
        choices=[
            ("all", "Everyone"),
            ("male", "Men"),
            ("female", "Women"),
            ("non_binary", "Non-Binary"),
        ],
        default="all",
    )
    relationship_goal = SelectField(
        "Relationship Goal",
        choices=[
            ("", "Select Goal"),
            ("friendship", "Friendship"),
            ("casual_dating", "Casual Dating"),
            ("serious_relationship", "Serious Relationship"),
            ("marriage", "Marriage"),
        ],
    )
    occupation = StringField(
        "Occupation",
        validators=[
            Optional(),
            Length(max=100, message="Occupation must be less than 100 characters"),
        ],
    )
    visibility = BooleanField("Make Profile Public", default=True)
