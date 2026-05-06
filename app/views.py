"""
Main application views and API endpoints.

This module contains all the Flask blueprint routes for the main application,
including authentication, user management, profile operations, and other core functionality.
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
from app.models import Profile, User, Match, Like, Bookmark

bp = Blueprint("main", __name__)

# Rate limiting storage (in production, use Redis)
rate_limit_store = {}


def rate_limit(max_requests=5, window_seconds=300):
    """
    Rate limiting decorator for API endpoints.

    Args:
        max_requests: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds for rate limiting

    Returns:
        Decorator function that enforces rate limits on the wrapped endpoint
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_app.config.get("TESTING"):
                return f(*args, **kwargs)

            # Get client identifier (IP or user_id)
            client_id = request.remote_addr
            if hasattr(g, "user") and g.user:
                client_id = f"user_{g.user.user_id}"

            current_time = time.time()
            window_key = (
                f"{client_id}:{request.endpoint}:{int(current_time // window_seconds)}"
            )

            # Check rate limit
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

            # Increment counter
            if window_key not in rate_limit_store:
                rate_limit_store[window_key] = (0, current_time)

            request_count, _ = rate_limit_store[window_key]
            rate_limit_store[window_key] = (request_count + 1, current_time)

            # Clean old entries
            cutoff = current_time - (window_seconds * 2)
            rate_limit_store.update(
                {k: v for k, v in rate_limit_store.items() if v[1] > cutoff}
            )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def generate_token(user_id, token_type="auth", expires_days=7):
    """Generate JWT token with configurable expiration"""
    payload = {
        "user_id": user_id,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def verify_token(token, token_type="auth"):
    """Verify and decode JWT token"""
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
    """Get user from JWT token in Authorization header"""
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


@bp.route("/")
def index():
    return jsonify(message="Welcome to DriftDater API", version="1.0")


@bp.route("/api/auth/register", methods=["POST"])
@rate_limit(max_requests=5, window_seconds=3600)  # 5 registrations per hour
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Validate password strength
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

    verify_url = (
        f"{current_app.config['FRONTEND_URL']}/verify/{user.verification_token}"
    )

    email_body = f"""
    <html>
    <body>
        <h2>Welcome to DriftDater!</h2>
        <p>Thank you for registering. Please verify your email by clicking the link below:</p>
        <p><a href="{verify_url}" style="display: inline-block; padding: 12px 24px; background-color: #10b981; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">Verify Email</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #6b7280;">{verify_url}</p>
        <hr style="margin: 24px 0; border: none; border-top: 1px solid #e5e7eb;">
        <p style="color: #9ca3af; font-size: 14px;">This link will expire in 24 hours.</p>
    </body>
    </html>
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


@bp.route("/api/auth/verify/<token>", methods=["GET"])
@rate_limit(max_requests=10, window_seconds=3600)
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return jsonify({"error": "Invalid verification token"}), 404

    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200

    # Check token expiration (24 hours)
    # Note: In production, store token expiry in the database
    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    return jsonify({"message": "Email verified successfully. You can now log in."}), 200


@bp.route("/api/auth/login", methods=["POST"])
@rate_limit(max_requests=10, window_seconds=300)  # 10 login attempts per 5 minutes
def login():
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
        # Log failed login attempt (for security monitoring)
        print(f"[SECURITY] Failed login attempt for email: {form.email.data}")
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


@bp.route("/api/auth/logout", methods=["POST"])
def logout():
    # In production, add token to blacklist
    # For now, just return success
    return jsonify({"message": "Logged out successfully"}), 200


@bp.route("/api/auth/resend-verification", methods=["POST"])
@rate_limit(max_requests=3, window_seconds=3600)  # 3 requests per hour
def resend_verification():
    data = request.get_json()

    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"].strip().lower()

    # Validate email format
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"error": "Invalid email format"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        # Don't reveal if email exists or not (security best practice)
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

    # Generate new verification token
    import secrets

    user.verification_token = secrets.token_urlsafe(32)
    db.session.flush()

    verify_url = (
        f"{current_app.config['FRONTEND_URL']}/verify/{user.verification_token}"
    )

    email_body = f"""
    <html>
    <body>
        <h2>Verify Your DriftDater Account</h2>
        <p>You requested to resend the verification email. Click the link below to verify your account:</p>
        <p><a href="{verify_url}" style="display: inline-block; padding: 12px 24px; background-color: #10b981; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">Verify Email</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #6b7280;">{verify_url}</p>
        <hr style="margin: 24px 0; border: none; border-top: 1px solid #e5e7eb;">
        <p style="color: #9ca3af; font-size: 14px;">This link will expire in 24 hours.</p>
        <p style="color: #9ca3af; font-size: 14px;">If you didn't request this, you can safely ignore this email.</p>
    </body>
    </html>
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


@bp.route("/api/auth/forgot-password", methods=["POST"])
@rate_limit(max_requests=5, window_seconds=3600)
def forgot_password():
    data = request.get_json()

    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"].strip().lower()

    # Validate email format
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


@bp.route("/api/auth/reset-password", methods=["POST"])
@rate_limit(max_requests=5, window_seconds=3600)
def reset_password():
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

    # Validate password strength
    password_check = validate_password_strength(password)
    if not password_check["is_valid"]:
        return jsonify({"errors": {"password": password_check["errors"]}}), 400

    # Verify reset token
    payload = verify_token(token, token_type="reset")
    if not payload:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    user = db.session.get(User, payload["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update password
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


@bp.route("/api/auth/refresh", methods=["POST"])
@rate_limit(max_requests=10, window_seconds=60)
def refresh_token():
    """Refresh authentication token"""
    data = request.get_json()

    if not data or "user_id" not in data:
        return jsonify({"error": "User ID is required"}), 400

    user = db.session.get(User, data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 401

    # Generate new token
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


@bp.route("/api/auth/me", methods=["GET"])
def get_current_user():
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile_name = None
    profile_picture = None
    if user.profile:
        profile_name = user.profile.name
        profile_picture = user.profile.profile_picture

    return (
        jsonify(
            {
                "id": user.user_id,
                "email": user.email,
                "is_verified": user.is_verified,
                "has_profile": user.profile is not None,
                "name": profile_name,
                "profile_picture": profile_picture,
            }
        ),
        200,
    )


@bp.route("/api/profile", methods=["GET"])
def get_profile():
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify(profile.to_dict()), 200


@bp.route("/api/profile", methods=["POST"])
def create_profile():
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    existing = Profile.query.filter_by(user_id=user.user_id).first()
    if existing:
        return jsonify({"error": "Profile already exists. Use PUT to update."}), 400

    data = request.get_json() or {}
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
        interests=interests_list,
        gender=form.gender.data,
        gender_preference=form.gender_preference.data,
        relationship_goal=form.relationship_goal.data,
        occupation=form.occupation.data,
        visibility=form.visibility.data,
        location=location,
    )

    db.session.add(profile)
    db.session.commit()

    return jsonify(profile.to_dict()), 201


@bp.route("/api/profile", methods=["PUT"])
def update_profile():
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found. Create one first."}), 404

    data = request.get_json() or {}
    data["interests"] = data.get("interests", [])

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

    if file and allowed_file(file.filename):
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

        return (
            jsonify({"message": "Profile picture uploaded", "filename": filename}),
            200,
        )

    return jsonify({"error": "Invalid file type"}), 400


@bp.route("/api/profile/<int:user_id>", methods=["GET"])
def view_other_profile(user_id):
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

@bp.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
