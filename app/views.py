"""
Main application views and API endpoints.

This module contains all the Flask blueprint routes for the main application,
including authentication, user management, profile operations, and search/discovery.

Implemented features
--------------------
USER AUTHENTICATION & PROFILE MANAGEMENT
  POST /api/auth/register          – Register with email validation
  GET  /api/auth/verify/<token>    – Email verification
  POST /api/auth/login             – Secure login (bcrypt)
  POST /api/auth/logout            – Logout
  POST /api/auth/resend-verification
  POST /api/auth/forgot-password
  POST /api/auth/reset-password
  POST /api/auth/refresh
  GET  /api/auth/me                – Current user info
  POST /api/auth/change-password   – Change password (requires current password)
  DELETE /api/auth/account         – Delete own account

  GET  /api/profile                – Get own profile
  POST /api/profile                – Create profile
  PUT  /api/profile                – Update profile (incl. location, age prefs)
  POST /api/profile/picture        – Upload profile picture
  GET  /api/profile/<user_id>      – View another user's public profile

SEARCH & DISCOVERY
  GET  /api/search                 – Search with query-string params (GET)
  POST /api/search                 – Search with JSON body (POST)
  GET  /api/search/suggestions     – Auto-complete interest suggestions
"""

import os
import re
import time
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.utils import secure_filename

from app import bcrypt, db
from app.email_utils import send_email
from app.forms import LoginForm, ProfileForm, RegistrationForm
from app.models import Bookmark, Like, Match, Profile, User

bp = Blueprint("main", __name__)

# ---------------------------------------------------------------------------
# Rate limiting (in-process; use Redis in production)
# ---------------------------------------------------------------------------
rate_limit_store = {}


def rate_limit(max_requests=5, window_seconds=300):
    """
    Rate-limiting decorator.

    Args:
        max_requests: Maximum allowed requests within the window.
        window_seconds: Duration of the time window in seconds.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_app.config.get("TESTING"):
                return f(*args, **kwargs)

            client_id = request.remote_addr
            if hasattr(g, "user") and g.user:
                client_id = f"user_{g.user.user_id}"

            current_time = time.time()
            window_key = (
                f"{client_id}:{request.endpoint}:{int(current_time // window_seconds)}"
            )

            if window_key in rate_limit_store:
                request_count, _ = rate_limit_store[window_key]
                if request_count >= max_requests:
                    return (
                        jsonify(
                            {
                                "error": "Too many requests. Please try again later.",
                                "retry_after": window_seconds,
                            }
                        ),
                        429,
                    )

            if window_key not in rate_limit_store:
                rate_limit_store[window_key] = (0, current_time)

            request_count, _ = rate_limit_store[window_key]
            rate_limit_store[window_key] = (request_count + 1, current_time)

            cutoff = current_time - (window_seconds * 2)
            rate_limit_store.update(
                {k: v for k, v in rate_limit_store.items() if v[1] > cutoff}
            )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------


def generate_token(user_id, token_type="auth", expires_days=7):
    """Generate a signed JWT with configurable expiration."""
    payload = {
        "user_id": user_id,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def verify_token(token, token_type="auth"):
    """Verify and decode a JWT; returns payload dict or None."""
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        if payload.get("type") != token_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def validate_password_strength(password):
    """Validate password strength with detailed feedback"""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")

    return {"is_valid": len(errors) == 0, "errors": errors}


def allowed_file(filename):
    allowed = current_app.config.get(
        "ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"}
    )
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def get_user_from_token():
    """Extract and validate the Bearer token; return User or None."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        user = db.session.get(User, payload["user_id"])
        return user
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Email helper
# ---------------------------------------------------------------------------


def send_email(to_email, subject, body):
    """Send an HTML email via SMTP (falls back to console log if unconfigured)."""
    time.sleep(0.5)  # minimal anti-spam delay

    try:
        smtp_host = current_app.config.get("MAILTRAP_SMTP_HOST")
        smtp_port = current_app.config.get("MAILTRAP_SMTP_PORT")
        smtp_user = current_app.config.get("MAILTRAP_SMTP_USER")
        smtp_pass = current_app.config.get("MAILTRAP_SMTP_PASS")
        from_email = current_app.config.get(
            "MAILTRAP_FROM_EMAIL", "noreply@driftdater.app"
        )

        if not smtp_user or not smtp_pass:
            print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}")
            print(f"[MOCK EMAIL] Body (first 200 chars): {body[:200]}")
            return True

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL] Sent to {to_email}")
        return True
    except Exception as exc:
        print(f"[EMAIL ERROR] {exc}")
        return False


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_password_strength(password):
    """Return dict with is_valid flag and list of error messages."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    return {"is_valid": len(errors) == 0, "errors": errors}


def allowed_file(filename):
    """Check whether an uploaded filename has an allowed image extension."""
    allowed = current_app.config.get(
        "ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"}
    )
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


@bp.route("/")
def index():
    return jsonify(message="Welcome to DriftDater API", version="1.0")


# ===========================================================================
# USER AUTHENTICATION & PROFILE MANAGEMENT
# ===========================================================================

# --- Registration -----------------------------------------------------------


@bp.route("/api/auth/register", methods=["POST"])
@rate_limit(max_requests=5, window_seconds=3600)
def register():
    """
    Register a new user account.

    Body (JSON):
        email (str): Unique email address
        password (str): Password meeting strength requirements
        confirm_password (str): Must match password

    Returns:
        201 – Registration successful; verification email sent
        400 – Validation error or email already taken
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Password strength check before WTForms so we get descriptive feedback
    if "password" in data:
        password_check = validate_password_strength(data["password"])
        if not password_check["is_valid"]:
            return jsonify({"errors": {"password": password_check["errors"]}}), 400

    form = RegistrationForm(data=data)
    if not form.validate():
        return jsonify({"errors": form.errors}), 400

    if User.query.filter_by(email=form.email.data).first():
        return jsonify({"errors": {"email": ["This email is already registered"]}}), 400

    password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
    user = User(email=form.email.data, password_hash=password_hash)
    db.session.add(user)
    db.session.flush()

    # Build verification URL
    base_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    verify_url = f"{base_url}/verify/{user.verification_token}"

    email_body = f"""
    <html><body>
        <h2>Welcome to DriftDater!</h2>
        <p>Thank you for registering. Please verify your email by clicking the link below:</p>
        <p><a href="{verify_url}" style="display:inline-block;padding:12px 24px;
            background:#10b981;color:#fff;text-decoration:none;border-radius:8px;
            font-weight:600;">Verify Email</a></p>
        <p>Or paste this link in your browser:<br>
        <span style="word-break:break-all;color:#6b7280;">{verify_url}</span></p>
        <hr style="margin:24px 0;border:none;border-top:1px solid #e5e7eb;">
        <p style="color:#9ca3af;font-size:14px;">This link expires in 24 hours.</p>
    </body></html>
    """

    if not send_email(user.email, "Verify your DriftDater account", email_body):
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Registration email could not be sent. Please check email delivery configuration and try again."
                }
            ),
            503,
        )

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Registration successful. Please check your email to verify your account.",
                "user_id": user.user_id,
            }
        ),
        201,
    )


# --- Email verification -----------------------------------------------------


@bp.route("/api/auth/verify/<token>", methods=["GET"])
@rate_limit(max_requests=10, window_seconds=3600)
def verify_email(token):
    """Verify a user's email address via the token sent during registration."""
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return jsonify({"error": "Invalid verification token"}), 404

    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200

    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    return jsonify({"message": "Email verified successfully. You can now log in."}), 200


# --- Login ------------------------------------------------------------------


@bp.route("/api/auth/login", methods=["POST"])
@rate_limit(max_requests=10, window_seconds=300)
def login():
    """
    Authenticate a verified user and return a JWT.

    Body (JSON):
        email (str)
        password (str)

    Returns:
        200 – Login successful with token and user info
        401 – Invalid credentials or unverified email
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    form = LoginForm(data=data)
    if not form.validate():
        return jsonify({"errors": form.errors}), 400

    user = User.query.filter_by(email=form.email.data).first()

    if not user or not bcrypt.check_password_hash(
        user.password_hash, form.password.data
    ):
        print(f"[SECURITY] Failed login attempt for: {form.email.data}")
        return jsonify({"errors": {"general": ["Invalid email or password"]}}), 401

    if not user.is_verified:
        return (
            jsonify(
                {
                    "errors": {
                        "general": [
                            "Please verify your email before logging in. Check your inbox."
                        ]
                    }
                }
            ),
            401,
        )

    # Update last_active timestamp
    user.last_active = datetime.now(timezone.utc)
    db.session.commit()

    token = generate_token(user.user_id)

    return (
        jsonify(
            {
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user.user_id,
                    "email": user.email,
                    "is_verified": user.is_verified,
                    "has_profile": user.profile is not None,
                },
            }
        ),
        200,
    )


# --- Logout -----------------------------------------------------------------


@bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """
    Logout the current user.

    In a stateless JWT setup this is a client-side operation; the server
    acknowledges the request. Extend with a token blacklist for stricter control.
    """
    return jsonify({"message": "Logged out successfully"}), 200


# --- Resend verification email ----------------------------------------------


@bp.route("/api/auth/resend-verification", methods=["POST"])
@rate_limit(max_requests=3, window_seconds=3600)
def resend_verification():
    """Resend the email verification link to an unverified account."""
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"].strip().lower()
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"error": "Invalid email format"}), 400

    user = User.query.filter_by(email=email).first()

    # Security: don't reveal whether email is registered
    if not user:
        return (
            jsonify(
                {
                    "message": "If an account exists with this email, a verification link has been sent."
                }
            ),
            200,
        )

    if user.is_verified:
        return jsonify({"error": "Email is already verified"}), 400

    import secrets as _secrets

    user.verification_token = _secrets.token_urlsafe(32)
    db.session.commit()

    base_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    verify_url = f"{base_url}/verify/{user.verification_token}"

    email_body = f"""
    <html><body>
        <h2>Verify Your DriftDater Account</h2>
        <p>Click the link below to verify your account:</p>
        <p><a href="{verify_url}" style="display:inline-block;padding:12px 24px;
            background:#10b981;color:#fff;text-decoration:none;border-radius:8px;
            font-weight:600;">Verify Email</a></p>
        <p style="color:#9ca3af;font-size:14px;">Link expires in 24 hours.</p>
    </body></html>
    """

    if not send_email(user.email, "Resend: Verify your DriftDater account", email_body):
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Verification email could not be sent. Please check email delivery configuration and try again."
                }
            ),
            503,
        )

    db.session.commit()

    return (
        jsonify({"message": "Verification email sent. Please check your inbox."}),
        200,
    )


# --- Forgot password --------------------------------------------------------


@bp.route("/api/auth/forgot-password", methods=["POST"])
@rate_limit(max_requests=5, window_seconds=3600)
def forgot_password():
    """Send a password reset link to the user's verified email."""
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"].strip().lower()
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"error": "Invalid email format"}), 400

    user = User.query.filter_by(email=email).first()

    # Don't reveal if email exists (security best practice)
    if not user:
        return (
            jsonify(
                {
                    "message": "If an account exists with this email, a password reset link has been sent."
                }
            ),
            200,
        )

    # Generate password reset token
    import secrets

    secrets.token_urlsafe(32)

    # Store token hash in database (in production, create a PasswordResetToken model)
    # For now, we'll encode it in JWT
    reset_jwt = generate_token(user.user_id, token_type="reset", expires_days=1)

    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={reset_jwt}"

    email_body = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>You requested to reset your password. Click the link below to create a new password:</p>
        <p><a href="{reset_url}" style="display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">Reset Password</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #6b7280;">{reset_url}</p>
        <hr style="margin: 24px 0; border: none; border-top: 1px solid #e5e7eb;">
        <p style="color: #9ca3af; font-size: 14px;">This link will expire in 1 hour.</p>
        <p style="color: #9ca3af; font-size: 14px;">If you didn't request this, you can safely ignore this email and your password will remain unchanged.</p>
    </body>
    </html>
    """

    if not send_email(user.email, "Password Reset Request", email_body):
        return jsonify({"error": "Password reset email could not be sent."}), 503

    return (
        jsonify(
            {
                "message": "If an account exists with this email, a password reset link has been sent."
            }
        ),
        200,
    )

    if not user:
        return _generic_response

    # Short-lived reset token (1 day)
    reset_jwt = generate_token(user.user_id, token_type="reset", expires_days=1)
    base_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    reset_url = f"{base_url}/reset-password?token={reset_jwt}"

    email_body = f"""
    <html><body>
        <h2>Password Reset Request</h2>
        <p>Click the link below to create a new password:</p>
        <p><a href="{reset_url}" style="display:inline-block;padding:12px 24px;
            background:#3b82f6;color:#fff;text-decoration:none;border-radius:8px;
            font-weight:600;">Reset Password</a></p>
        <p style="color:#9ca3af;font-size:14px;">Link expires in 1 hour.</p>
        <p style="color:#9ca3af;font-size:14px;">
            If you didn't request this, you can safely ignore this email.
        </p>
    </body></html>
    """
    send_email(user.email, "DriftDater – Password Reset Request", email_body)

    return _generic_response


# --- Reset password ---------------------------------------------------------


@bp.route("/api/auth/reset-password", methods=["POST"])
@rate_limit(max_requests=5, window_seconds=3600)
def reset_password():
    """
    Set a new password using a valid reset JWT.

    Body (JSON):
        token (str): Reset token from email link
        password (str): New password
        confirm_password (str): Must match password
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request data is required"}), 400

    token = data.get("token")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if not token:
        return jsonify({"error": "Reset token is required"}), 400
    if not password or not confirm_password:
        return jsonify({"error": "Password and confirm password are required"}), 400
    if password != confirm_password:
        return (
            jsonify({"errors": {"confirm_password": ["Passwords do not match"]}}),
            400,
        )

    password_check = validate_password_strength(password)
    if not password_check["is_valid"]:
        return jsonify({"errors": {"password": password_check["errors"]}}), 400

    payload = verify_token(token, token_type="reset")
    if not payload:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    user = db.session.get(User, payload["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Password reset successfully. You can now log in with your new password."
            }
        ),
        200,
    )


# --- Change password (authenticated) ---------------------------------------


@bp.route("/api/auth/change-password", methods=["POST"])
def change_password():
    """
    Change the authenticated user's password.

    Body (JSON):
        current_password (str): The user's existing password
        new_password (str): The desired new password
        confirm_password (str): Must match new_password

    Returns:
        200 – Password changed successfully
        400 – Validation error
        401 – Authentication required or wrong current password
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not current_password:
        return (
            jsonify({"errors": {"current_password": ["Current password is required"]}}),
            400,
        )
    if not new_password:
        return jsonify({"errors": {"new_password": ["New password is required"]}}), 400
    if not confirm_password:
        return (
            jsonify(
                {"errors": {"confirm_password": ["Please confirm your new password"]}}
            ),
            400,
        )

    # Verify current password
    if not bcrypt.check_password_hash(user.password_hash, current_password):
        return (
            jsonify({"errors": {"current_password": ["Incorrect current password"]}}),
            401,
        )

    if new_password == current_password:
        return (
            jsonify(
                {
                    "errors": {
                        "new_password": [
                            "New password must differ from the current one"
                        ]
                    }
                }
            ),
            400,
        )

    if new_password != confirm_password:
        return (
            jsonify({"errors": {"confirm_password": ["Passwords do not match"]}}),
            400,
        )

    strength = validate_password_strength(new_password)
    if not strength["is_valid"]:
        return jsonify({"errors": {"new_password": strength["errors"]}}), 400

    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200


# --- Refresh token ----------------------------------------------------------


@bp.route("/api/auth/refresh", methods=["POST"])
@rate_limit(max_requests=10, window_seconds=60)
def refresh_token():
    """Issue a fresh JWT for the given user_id (used for silent token renewal)."""
    data = request.get_json()
    if not data or "user_id" not in data:
        return jsonify({"error": "User ID is required"}), 400

    user = db.session.get(User, data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 401

    new_token = generate_token(user.user_id)

    return (
        jsonify(
            {
                "token": new_token,
                "user": {
                    "id": user.user_id,
                    "email": user.email,
                    "is_verified": user.is_verified,
                    "has_profile": user.profile is not None,
                },
            }
        ),
        200,
    )


# --- Current user -----------------------------------------------------------


@bp.route("/api/auth/me", methods=["GET"])
def get_current_user():
    """Return the authenticated user's basic info."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile_name = None
    profile_picture = None
    profile_location = None
    if user.profile:
        profile_name = user.profile.name
        profile_picture = user.profile.profile_picture
        profile_location = user.profile.location

    return (
        jsonify(
            {
                "id": user.user_id,
                "email": user.email,
                "is_verified": user.is_verified,
                "has_profile": user.profile is not None,
                "name": profile_name,
                "profile_picture": profile_picture,
                "location": profile_location,
            }
        ),
        200,
    )


# --- Delete account ---------------------------------------------------------


@bp.route("/api/auth/account", methods=["DELETE"])
def delete_account():
    """
    Permanently delete the authenticated user's account and all associated data.

    Body (JSON):
        password (str): Must be confirmed to prevent accidental deletion

    Returns:
        200 – Account deleted
        401 – Authentication required or wrong password
        400 – Missing password
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json() or {}
    password = data.get("password")

    if not password:
        return (
            jsonify(
                {"error": "Password confirmation is required to delete your account"}
            ),
            400,
        )

    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Incorrect password"}), 401

    # Cascade delete handles profile, notifications, and related records via model relationships.
    # We also manually clean up likes and matches referencing this user since they do not use cascade.
    Like.query.filter(
        (Like.from_user_id == user.user_id) | (Like.to_user_id == user.user_id)
    ).delete(synchronize_session=False)

    Match.query.filter(
        (Match.user1_id == user.user_id) | (Match.user2_id == user.user_id)
    ).delete(synchronize_session=False)

    Bookmark.query.filter(
        (Bookmark.user_id == user.user_id)
        | (Bookmark.bookmarked_user_id == user.user_id)
    ).delete(synchronize_session=False)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Account deleted successfully"}), 200


# ===========================================================================
# PROFILE ENDPOINTS
# ===========================================================================


@bp.route("/api/profile", methods=["GET"])
def get_profile():
    """Return the authenticated user's own profile."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify(profile.to_dict()), 200


@bp.route("/api/profile", methods=["POST"])
def create_profile():
    """
    Create a new profile for the authenticated user.

    Body (JSON):
        name (str): Display name
        age (int): Age (≥18)
        bio (str, optional): Biography up to 500 chars
        location (str, optional): City / parish / country
        interests (list|str): At least 3 interests
        gender (str): Gender identity
        gender_preference (str): Preferred partner gender
        relationship_goal (str): What the user is looking for
        occupation (str, optional): Job/profession
        preferred_age_min (int, optional): Minimum preferred match age
        preferred_age_max (int, optional): Maximum preferred match age
        visibility (bool): True = public (default)

    Returns:
        201 – Profile created
        400 – Validation error or profile already exists
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    existing = Profile.query.filter_by(user_id=user.user_id).first()
    if existing:
        return jsonify({"error": "Profile already exists. Use PUT to update."}), 400

    data = request.get_json() or {}

    # Normalise interests for WTForms (expects comma-separated string)
    interests_raw = data.get("interests", [])
    if isinstance(interests_raw, list):
        data["interests"] = ", ".join(interests_raw)
    # else it's already a string

    form = ProfileForm(data=data)
    if not form.validate():
        return jsonify({"errors": form.errors}), 400

    # Parse interests list
    if isinstance(interests_raw, list):
        interests_list = [i.strip() for i in interests_raw if i.strip()]
    else:
        interests_list = [
            i.strip() for i in form.interests.data.split(",") if i.strip()
        ]

    if len(interests_list) < 3:
        return (
            jsonify({"errors": {"interests": ["Please add at least 3 interests"]}}),
            400,
        )

    # Age preference validation
    preferred_age_min = data.get("preferred_age_min", 18)
    preferred_age_max = data.get("preferred_age_max", 50)
    try:
        preferred_age_min = int(preferred_age_min)
        preferred_age_max = int(preferred_age_max)
    except (TypeError, ValueError):
        preferred_age_min, preferred_age_max = 18, 50

    if preferred_age_min < 18:
        preferred_age_min = 18
    if preferred_age_max > 120:
        preferred_age_max = 120
    if preferred_age_min > preferred_age_max:
        return (
            jsonify(
                {
                    "errors": {
                        "preferred_age_min": ["Minimum age cannot exceed maximum age"]
                    }
                }
            ),
            400,
        )

    location = (data.get("location") or "").strip() or None

    profile = Profile(
        user_id=user.user_id,
        name=form.name.data,
        age=form.age.data,
        bio=form.bio.data,
        location=location,
        interests=interests_list,
        gender=form.gender.data,
        gender_preference=form.gender_preference.data,
        relationship_goal=form.relationship_goal.data,
        occupation=form.occupation.data,
        preferred_age_min=preferred_age_min,
        preferred_age_max=preferred_age_max,
        visibility=form.visibility.data,
    )

    db.session.add(profile)
    db.session.commit()

    return jsonify(profile.to_dict()), 201


@bp.route("/api/profile", methods=["PUT"])
def update_profile():
    """
    Update the authenticated user's existing profile.

    All fields are optional — only provided fields are updated.

    Body (JSON): same fields as POST /api/profile

    Returns:
        200 – Profile updated
        404 – Profile not found
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not profile:
        return jsonify({"error": "Profile not found. Create one first."}), 404

    data = request.get_json() or {}

    if "name" in data and data["name"]:
        profile.name = str(data["name"]).strip()

    if "age" in data and data["age"] is not None:
        try:
            age = int(data["age"])
            if age < 18:
                return (
                    jsonify({"errors": {"age": ["You must be at least 18 years old"]}}),
                    400,
                )
            profile.age = age
        except (TypeError, ValueError):
            return jsonify({"errors": {"age": ["Invalid age value"]}}), 400

    if "bio" in data:
        profile.bio = data["bio"]

    if "location" in data:
        profile.location = (data["location"] or "").strip() or None

    if "interests" in data and data["interests"]:
        raw = data["interests"]
        if isinstance(raw, list):
            interests_list = [i.strip() for i in raw if str(i).strip()]
        else:
            interests_list = [i.strip() for i in str(raw).split(",") if i.strip()]
        if len(interests_list) < 3:
            return (
                jsonify({"errors": {"interests": ["Please add at least 3 interests"]}}),
                400,
            )
        profile.interests = interests_list

    if "gender" in data and data["gender"]:
        profile.gender = data["gender"]

    if "gender_preference" in data and data["gender_preference"]:
        profile.gender_preference = data["gender_preference"]

    if "relationship_goal" in data and data["relationship_goal"]:
        profile.relationship_goal = data["relationship_goal"]

    if "occupation" in data:
        profile.occupation = data["occupation"] if data["occupation"] else None

    if "visibility" in data:
        profile.visibility = bool(data["visibility"])

    # Age preferences
    if "preferred_age_min" in data and data["preferred_age_min"] is not None:
        try:
            val = int(data["preferred_age_min"])
            profile.preferred_age_min = max(18, val)
        except (TypeError, ValueError):
            pass

    if "preferred_age_max" in data and data["preferred_age_max"] is not None:
        try:
            val = int(data["preferred_age_max"])
            profile.preferred_age_max = min(120, val)
        except (TypeError, ValueError):
            pass

    if profile.preferred_age_min > profile.preferred_age_max:
        return (
            jsonify(
                {
                    "errors": {
                        "preferred_age_min": ["Minimum age cannot exceed maximum age"]
                    }
                }
            ),
            400,
        )

    db.session.commit()

    return jsonify(profile.to_dict()), 200


@bp.route("/api/profile/picture", methods=["POST"])
def upload_picture():
    """
    Upload a profile picture for the authenticated user.

    Multipart form field: file

    Returns:
        200 – Upload successful with filename
        400 – No file / invalid type / profile missing
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not profile:
        return jsonify({"error": "Create a profile first"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file or not allowed_file(file.filename):
        return (
            jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp"}),
            400,
        )

    filename = secure_filename(f"user_{user.user_id}_{file.filename}")
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "./uploads")
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), upload_folder
        )
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    profile.profile_picture = filename
    db.session.commit()

    return jsonify({"message": "Profile picture uploaded", "filename": filename}), 200


@bp.route("/api/profile/<int:user_id>", methods=["GET"])
def view_other_profile(user_id):
    """
    View another user's profile.

    Private profiles are only accessible by the profile owner.

    Returns:
        200 – Profile data
        403 – Profile is private
        404 – Profile not found
    """
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    if not profile.visibility:
        user = get_user_from_token()
        if not user or user.user_id != user_id:
            return jsonify({"error": "This profile is private"}), 403

    return jsonify(profile.to_dict()), 200

# ===========================================================================
# SEARCH & DISCOVERY
# ===========================================================================


@bp.route("/api/search", methods=["GET"])
def search_get():
    """
    Search profiles using query-string parameters (GET convenience endpoint).

    Query Parameters:
        q (str): Text search against name and bio
        location (str): Filter by location (case-insensitive, partial match)
        age_min (int): Minimum age
        age_max (int): Maximum age
        interests (str): Comma-separated list of interests (all must match)
        gender (str): Filter by gender
        relationship_goal (str): Filter by relationship goal
        occupation (str): Partial match on occupation
        sort_by (str): newest | oldest | age_asc | age_desc | similarity
        page (int): Page number (1-based, default 1)
        per_page (int): Results per page (default 20, max 50)

    Returns:
        200 – Paginated list of matching profiles with match scores
        401 – Authentication required
        400 – No profile found for current user
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    current_profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not current_profile:
        return jsonify({"error": "Create a profile first"}), 400

    # Parse query-string params
    data = {
        "q": request.args.get("q", "").strip(),
        "location": request.args.get("location", "").strip(),
        "age_min": request.args.get("age_min"),
        "age_max": request.args.get("age_max"),
        "interests": [
            i.strip() for i in request.args.get("interests", "").split(",") if i.strip()
        ],
        "gender": request.args.get("gender", "").strip(),
        "relationship_goal": request.args.get("relationship_goal", "").strip(),
        "occupation": request.args.get("occupation", "").strip(),
        "sort_by": request.args.get("sort_by", "newest"),
        "page": request.args.get("page", 1),
        "per_page": request.args.get("per_page", 20),
    }

    return _execute_search(user, current_profile, data)


@bp.route("/api/search", methods=["POST"])
def search_post():
    """
    Search profiles using a JSON body (POST endpoint for richer filtering).

    Body (JSON): same fields as GET /api/search query parameters.

    Returns:
        200 – Paginated list of matching profiles with match scores
        401 – Authentication required
        400 – No profile found for current user
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    current_profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not current_profile:
        return jsonify({"error": "Create a profile first"}), 400

    data = request.get_json() or {}
    return _execute_search(user, current_profile, data)


def _execute_search(user, current_profile, data):
    """
    Core search logic shared by GET and POST endpoints.

    Applies text, location, age, interest, gender, relationship goal, and
    occupation filters then sorts and paginates results.

    Args:
        user: Authenticated User model instance
        current_profile: That user's Profile model instance
        data: Dict of filter/sort/pagination parameters

    Returns:
        Flask JSON response with paginated results and metadata.
    """
    from app.matches import (
        calculate_match_score,
    )  # avoid circular import at module level

    # --- Parse and coerce parameters ----------------------------------------
    q = str(data.get("q") or "").strip().lower()
    location = str(data.get("location") or "").strip().lower()

    try:
        age_min = int(data["age_min"]) if data.get("age_min") is not None else None
    except (TypeError, ValueError):
        age_min = None
    try:
        age_max = int(data["age_max"]) if data.get("age_max") is not None else None
    except (TypeError, ValueError):
        age_max = None

    interests = data.get("interests") or []
    if isinstance(interests, str):
        interests = [i.strip() for i in interests.split(",") if i.strip()]

    gender = str(data.get("gender") or "").strip()
    relationship_goal = str(data.get("relationship_goal") or "").strip()
    occupation = str(data.get("occupation") or "").strip().lower()
    sort_by = str(data.get("sort_by") or "newest").strip()

    try:
        page = max(1, int(data.get("page") or 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = min(50, max(1, int(data.get("per_page") or 20)))
    except (TypeError, ValueError):
        per_page = 20

    # --- Base query ---------------------------------------------------------
    # Exclude:  the requesting user, private profiles
    query = Profile.query.filter(
        Profile.user_id != user.user_id,
        Profile.visibility.is_(True),
    )

    # Text search – name or bio
    if q:
        like_expr = f"%{q}%"
        query = query.filter(
            db.or_(
                Profile.name.ilike(like_expr),
                Profile.bio.ilike(like_expr),
            )
        )

    # Location filter (case-insensitive, partial match)
    if location:
        query = query.filter(Profile.location.ilike(f"%{location}%"))

    # Age range
    if age_min is not None:
        query = query.filter(Profile.age >= age_min)
    if age_max is not None:
        query = query.filter(Profile.age <= age_max)

    # Gender
    if gender:
        query = query.filter(Profile.gender == gender)

    # Relationship goal
    if relationship_goal:
        query = query.filter(Profile.relationship_goal == relationship_goal)

    # Occupation (partial match)
    if occupation:
        query = query.filter(Profile.occupation.ilike(f"%{occupation}%"))

    # Interests – every listed interest must appear in the profile's JSON array
    # Using JSON contains check supported by SQLite / PostgreSQL via SQLAlchemy
    for interest in interests:
        query = query.filter(Profile.interests.contains(interest))

    # --- Sorting (pre-DB where possible) ------------------------------------
    if sort_by == "newest":
        query = query.order_by(Profile.created_at.desc())
    elif sort_by == "oldest":
        query = query.order_by(Profile.created_at.asc())
    elif sort_by == "age_asc":
        query = query.order_by(Profile.age.asc())
    elif sort_by == "age_desc":
        query = query.order_by(Profile.age.desc())
    # similarity / match_score are computed post-fetch and sorted in Python

    # --- Fetch all matching profiles (cap at 200 before scoring/paging) ----
    all_profiles = query.limit(200).all()

    # --- Score each profile -------------------------------------------------
    results = []
    for p in all_profiles:
        match_result = calculate_match_score(current_profile, p)
        profile_data = p.to_dict()
        profile_data["match_score"] = (
            match_result["score"] if isinstance(match_result, dict) else match_result
        )
        profile_data["match_details"] = (
            match_result.get("details", {}) if isinstance(match_result, dict) else {}
        )

        # Bookmark status
        bookmark = Bookmark.query.filter_by(
            user_id=user.user_id, bookmarked_user_id=p.user_id
        ).first()
        profile_data["is_bookmarked"] = bookmark is not None

        results.append(profile_data)

    # --- Post-fetch sort for similarity/match_score -------------------------
    if sort_by in ("similarity", "match_score"):
        results.sort(key=lambda x: x["match_score"], reverse=True)

    # --- Paginate in Python (avoids repeated DB queries) --------------------
    total = len(results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = results[start:end]

    return (
        jsonify(
            {
                "results": paginated,
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
                "filters_applied": {
                    "q": q or None,
                    "location": location or None,
                    "age_min": age_min,
                    "age_max": age_max,
                    "interests": interests or None,
                    "gender": gender or None,
                    "relationship_goal": relationship_goal or None,
                    "occupation": occupation or None,
                    "sort_by": sort_by,
                },
            }
        ),
        200,
    )


@bp.route("/api/search/suggestions", methods=["GET"])
def search_suggestions():
    """
    Return auto-complete suggestions for interests and locations.

    Query Parameters:
        type (str): 'interests' | 'locations' | 'occupations'
        q (str): Prefix to match (min 2 chars)

    Returns:
        200 – List of up to 10 matching suggestions
        400 – Invalid type or query too short
        401 – Authentication required
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    suggestion_type = request.args.get("type", "interests").strip()
    q = request.args.get("q", "").strip().lower()

    if len(q) < 2:
        return jsonify({"suggestions": []}), 200

    if suggestion_type not in ("interests", "locations", "occupations"):
        return (
            jsonify({"error": "type must be interests, locations, or occupations"}),
            400,
        )

    if suggestion_type == "locations":
        rows = (
            db.session.query(Profile.location)
            .filter(
                Profile.visibility.is_(True),
                Profile.location.isnot(None),
                Profile.location.ilike(f"%{q}%"),
            )
            .distinct()
            .limit(10)
            .all()
        )
        suggestions = [r.location for r in rows if r.location]

    elif suggestion_type == "occupations":
        rows = (
            db.session.query(Profile.occupation)
            .filter(
                Profile.visibility.is_(True),
                Profile.occupation.isnot(None),
                Profile.occupation.ilike(f"%{q}%"),
            )
            .distinct()
            .limit(10)
            .all()
        )
        suggestions = [r.occupation for r in rows if r.occupation]

    else:  # interests
        # Interests are stored as JSON arrays; we load all public profiles and
        # filter in Python (acceptable for moderate dataset sizes).
        all_interests = set()
        profiles = (
            Profile.query.filter(
                Profile.visibility.is_(True), Profile.interests.isnot(None)
            )
            .with_entities(Profile.interests)
            .limit(500)
            .all()
        )
        for (interests_json,) in profiles:
            if isinstance(interests_json, list):
                for interest in interests_json:
                    if q in interest.lower():
                        all_interests.add(interest)

        suggestions = sorted(all_interests)[:10]

    return (
        jsonify({"suggestions": suggestions, "type": suggestion_type, "query": q}),
        200,
    )

# ===========================================================================
# SEARCH & DISCOVERY
# ===========================================================================


@bp.route("/api/search", methods=["GET"])
def search_get():
    """
    Search profiles using query-string parameters (GET convenience endpoint).

    Query Parameters:
        q (str): Text search against name and bio
        location (str): Filter by location (case-insensitive, partial match)
        age_min (int): Minimum age
        age_max (int): Maximum age
        interests (str): Comma-separated list of interests (all must match)
        gender (str): Filter by gender
        relationship_goal (str): Filter by relationship goal
        occupation (str): Partial match on occupation
        sort_by (str): newest | oldest | age_asc | age_desc | similarity
        page (int): Page number (1-based, default 1)
        per_page (int): Results per page (default 20, max 50)

    Returns:
        200 – Paginated list of matching profiles with match scores
        401 – Authentication required
        400 – No profile found for current user
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    current_profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not current_profile:
        return jsonify({"error": "Create a profile first"}), 400

    # Parse query-string params
    data = {
        "q": request.args.get("q", "").strip(),
        "location": request.args.get("location", "").strip(),
        "age_min": request.args.get("age_min"),
        "age_max": request.args.get("age_max"),
        "interests": [
            i.strip() for i in request.args.get("interests", "").split(",") if i.strip()
        ],
        "gender": request.args.get("gender", "").strip(),
        "relationship_goal": request.args.get("relationship_goal", "").strip(),
        "occupation": request.args.get("occupation", "").strip(),
        "sort_by": request.args.get("sort_by", "newest"),
        "page": request.args.get("page", 1),
        "per_page": request.args.get("per_page", 20),
    }

    return _execute_search(user, current_profile, data)


@bp.route("/api/search", methods=["POST"])
def search_post():
    """
    Search profiles using a JSON body (POST endpoint for richer filtering).

    Body (JSON): same fields as GET /api/search query parameters.

    Returns:
        200 – Paginated list of matching profiles with match scores
        401 – Authentication required
        400 – No profile found for current user
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    current_profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not current_profile:
        return jsonify({"error": "Create a profile first"}), 400

    data = request.get_json() or {}
    return _execute_search(user, current_profile, data)


def _execute_search(user, current_profile, data):
    """
    Core search logic shared by GET and POST endpoints.

    Applies text, location, age, interest, gender, relationship goal, and
    occupation filters then sorts and paginates results.

    Args:
        user: Authenticated User model instance
        current_profile: That user's Profile model instance
        data: Dict of filter/sort/pagination parameters

    Returns:
        Flask JSON response with paginated results and metadata.
    """
    from app.matches import (
        calculate_match_score,
    )  # avoid circular import at module level

    # --- Parse and coerce parameters ----------------------------------------
    q = str(data.get("q") or "").strip().lower()
    location = str(data.get("location") or "").strip().lower()

    try:
        age_min = int(data["age_min"]) if data.get("age_min") is not None else None
    except (TypeError, ValueError):
        age_min = None
    try:
        age_max = int(data["age_max"]) if data.get("age_max") is not None else None
    except (TypeError, ValueError):
        age_max = None

    interests = data.get("interests") or []
    if isinstance(interests, str):
        interests = [i.strip() for i in interests.split(",") if i.strip()]

    gender = str(data.get("gender") or "").strip()
    relationship_goal = str(data.get("relationship_goal") or "").strip()
    occupation = str(data.get("occupation") or "").strip().lower()
    sort_by = str(data.get("sort_by") or "newest").strip()

    try:
        page = max(1, int(data.get("page") or 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = min(50, max(1, int(data.get("per_page") or 20)))
    except (TypeError, ValueError):
        per_page = 20

    # --- Base query ---------------------------------------------------------
    # Exclude:  the requesting user, private profiles
    query = Profile.query.filter(
        Profile.user_id != user.user_id,
        Profile.visibility.is_(True),
    )

    # Text search – name or bio
    if q:
        like_expr = f"%{q}%"
        query = query.filter(
            db.or_(
                Profile.name.ilike(like_expr),
                Profile.bio.ilike(like_expr),
            )
        )

    # Location filter (case-insensitive, partial match)
    if location:
        query = query.filter(Profile.location.ilike(f"%{location}%"))

    # Age range
    if age_min is not None:
        query = query.filter(Profile.age >= age_min)
    if age_max is not None:
        query = query.filter(Profile.age <= age_max)

    # Gender
    if gender:
        query = query.filter(Profile.gender == gender)

    # Relationship goal
    if relationship_goal:
        query = query.filter(Profile.relationship_goal == relationship_goal)

    # Occupation (partial match)
    if occupation:
        query = query.filter(Profile.occupation.ilike(f"%{occupation}%"))

    # Interests – every listed interest must appear in the profile's JSON array
    # Using JSON contains check supported by SQLite / PostgreSQL via SQLAlchemy
    for interest in interests:
        query = query.filter(Profile.interests.contains(interest))

    # --- Sorting (pre-DB where possible) ------------------------------------
    if sort_by == "newest":
        query = query.order_by(Profile.created_at.desc())
    elif sort_by == "oldest":
        query = query.order_by(Profile.created_at.asc())
    elif sort_by == "age_asc":
        query = query.order_by(Profile.age.asc())
    elif sort_by == "age_desc":
        query = query.order_by(Profile.age.desc())
    # similarity / match_score are computed post-fetch and sorted in Python

    # --- Fetch all matching profiles (cap at 200 before scoring/paging) ----
    all_profiles = query.limit(200).all()

    # --- Score each profile -------------------------------------------------
    results = []
    for p in all_profiles:
        match_result = calculate_match_score(current_profile, p)
        profile_data = p.to_dict()
        profile_data["match_score"] = (
            match_result["score"] if isinstance(match_result, dict) else match_result
        )
        profile_data["match_details"] = (
            match_result.get("details", {}) if isinstance(match_result, dict) else {}
        )

        # Bookmark status
        bookmark = Bookmark.query.filter_by(
            user_id=user.user_id, bookmarked_user_id=p.user_id
        ).first()
        profile_data["is_bookmarked"] = bookmark is not None

        results.append(profile_data)

    # --- Post-fetch sort for similarity/match_score -------------------------
    if sort_by in ("similarity", "match_score"):
        results.sort(key=lambda x: x["match_score"], reverse=True)

    # --- Paginate in Python (avoids repeated DB queries) --------------------
    total = len(results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = results[start:end]

    return (
        jsonify(
            {
                "results": paginated,
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
                "filters_applied": {
                    "q": q or None,
                    "location": location or None,
                    "age_min": age_min,
                    "age_max": age_max,
                    "interests": interests or None,
                    "gender": gender or None,
                    "relationship_goal": relationship_goal or None,
                    "occupation": occupation or None,
                    "sort_by": sort_by,
                },
            }
        ),
        200,
    )


@bp.route("/api/search/suggestions", methods=["GET"])
def search_suggestions():
    """
    Return auto-complete suggestions for interests and locations.

    Query Parameters:
        type (str): 'interests' | 'locations' | 'occupations'
        q (str): Prefix to match (min 2 chars)

    Returns:
        200 – List of up to 10 matching suggestions
        400 – Invalid type or query too short
        401 – Authentication required
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    suggestion_type = request.args.get("type", "interests").strip()
    q = request.args.get("q", "").strip().lower()

    if len(q) < 2:
        return jsonify({"suggestions": []}), 200

    if suggestion_type not in ("interests", "locations", "occupations"):
        return (
            jsonify({"error": "type must be interests, locations, or occupations"}),
            400,
        )

    if suggestion_type == "locations":
        rows = (
            db.session.query(Profile.location)
            .filter(
                Profile.visibility.is_(True),
                Profile.location.isnot(None),
                Profile.location.ilike(f"%{q}%"),
            )
            .distinct()
            .limit(10)
            .all()
        )
        suggestions = [r.location for r in rows if r.location]

    elif suggestion_type == "occupations":
        rows = (
            db.session.query(Profile.occupation)
            .filter(
                Profile.visibility.is_(True),
                Profile.occupation.isnot(None),
                Profile.occupation.ilike(f"%{q}%"),
            )
            .distinct()
            .limit(10)
            .all()
        )
        suggestions = [r.occupation for r in rows if r.occupation]

    else:  # interests
        # Interests are stored as JSON arrays; we load all public profiles and
        # filter in Python (acceptable for moderate dataset sizes).
        all_interests = set()
        profiles = (
            Profile.query.filter(
                Profile.visibility.is_(True), Profile.interests.isnot(None)
            )
            .with_entities(Profile.interests)
            .limit(500)
            .all()
        )
        for (interests_json,) in profiles:
            if isinstance(interests_json, list):
                for interest in interests_json:
                    if q in interest.lower():
                        all_interests.add(interest)

        suggestions = sorted(all_interests)[:10]

    return (
        jsonify({"suggestions": suggestions, "type": suggestion_type, "query": q}),
        200,
    )


# ===========================================================================
# Response headers
# ===========================================================================


@bp.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
