import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models import User


class TestRegistration:
    """Test user registration functionality."""

    def test_register_success(self, client):
        """User should be able to register with valid credentials."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
        )

        assert response.status_code == 201
        assert "user_id" in response.json
        assert "message" in response.json

    def test_register_duplicate_email(self, client):
        """Registration should fail if email is already registered."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
        )

        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
        )

        assert response.status_code == 400
        assert "email" in response.json.get("errors", {})

    def test_register_invalid_email(self, client):
        """Registration should fail with invalid email format."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
        )

        assert response.status_code == 400

    def test_register_password_mismatch(self, client):
        """Registration should fail if passwords don't match."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "confirm_password": "DifferentPass1!",
            },
        )

        assert response.status_code == 400

    def test_register_missing_email(self, client):
        """Registration should fail if email is missing."""
        response = client.post(
            "/api/auth/register",
            json={"password": "TestPass123!", "confirm_password": "TestPass123!"},
        )

        assert response.status_code == 400

    def test_register_missing_password(self, client):
        """Registration should fail if password is missing."""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "confirm_password": "TestPass123!"},
        )

        assert response.status_code == 400


class TestPasswordValidation:
    """Test password validation rules with parameterized tests."""

    @pytest.mark.parametrize(
        "password,should_fail,expected_error",
        [
            ("Ab1!", True, "8 characters"),  # Too short
            ("abcdefgh1!", True, "uppercase"),  # No uppercase
            ("ABCDEFGH1!", True, "lowercase"),  # No lowercase
            ("Abcdefgh!!", True, "number"),  # No number
            ("Abcdefgh123", True, "special"),  # No special char
            ("ValidPass1!", False, None),  # Valid
            ("Short1", True, "8 characters"),  # Very short
            ("NoSpecial1", True, "special"),  # No special character
            ("12345678A!", True, None),  # Starts with number (still valid)
        ],
    )
    def test_password_strength(self, client, password, should_fail, expected_error):
        """Test various password strength scenarios."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": f"test_{password[:8]}@example.com",
                "password": password,
                "confirm_password": password,
            },
        )

        if should_fail:
            assert response.status_code == 400
            assert "password" in response.json.get("errors", {})
        else:
            assert response.status_code == 201


class TestLogin:
    """Test user login functionality."""

    def test_login_success(self, client, app, verified_user):
        """User should be able to login with valid credentials."""
        response = client.post(
            "/api/auth/login",
            json={"email": verified_user["email"], "password": "TestPass123!"},
        )

        assert response.status_code == 200
        assert "token" in response.json
        assert "user" in response.json
        assert response.json["user"]["email"] == verified_user["email"]

    def test_login_wrong_password(self, client, app, verified_user):
        """Login should fail with incorrect password."""
        response = client.post(
            "/api/auth/login",
            json={"email": verified_user["email"], "password": "wrongpassword"},
        )

        assert response.status_code == 401

    def test_login_unverified_email(self, client, app):
        """Login should fail for unverified users."""
        client.post(
            "/api/auth/register",
            json={
                "email": "unverified@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
        )

        response = client.post(
            "/api/auth/login",
            json={"email": "unverified@example.com", "password": "TestPass123!"},
        )

        assert response.status_code == 401
        assert "verify" in response.json["errors"]["general"][0].lower()

    def test_login_nonexistent_user(self, client):
        """Login should fail for non-existent email."""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "TestPass123!"},
        )

        assert response.status_code == 401

    def test_login_missing_email(self, client):
        """Login should fail if email is missing."""
        response = client.post("/api/auth/login", json={"password": "TestPass123!"})

        assert response.status_code == 400

    def test_login_missing_password(self, client):
        """Login should fail if password is missing."""
        response = client.post("/api/auth/login", json={"email": "test@example.com"})

        assert response.status_code == 400

    def test_login_returns_user_data(self, client, app, verified_user):
        """Login should return user data including verification status."""
        response = client.post(
            "/api/auth/login",
            json={"email": verified_user["email"], "password": "TestPass123!"},
        )

        assert response.status_code == 200
        assert response.json["user"]["is_verified"]
        assert "has_profile" in response.json["user"]


class TestLogout:
    """Test user logout functionality."""

    def test_logout_success(self, client, verified_user):
        """User should be able to logout."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 200
        assert "Logged out" in response.json["message"]


class TestEmailVerification:
    """Test email verification functionality."""

    def test_verify_email_success(self, client, app):
        """Email verification should work with valid token."""
        client.post(
            "/api/auth/register",
            json={
                "email": "verify@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
        )

        with app.app_context():
            user = db.session.query(User).filter_by(email="verify@example.com").first()
            token = user.verification_token

        response = client.get(f"/api/auth/verify/{token}")

        assert response.status_code == 200
        assert "verified" in response.json["message"].lower()

    def test_verify_email_invalid_token(self, client):
        """Email verification should fail with invalid token."""
        response = client.get("/api/auth/verify/invalid_token_12345")

        assert response.status_code == 404

    def test_verify_email_already_verified(self, client, app, verified_user):
        """Verification should handle already verified users."""
        with app.app_context():
            user = (
                db.session.query(User).filter_by(email=verified_user["email"]).first()
            )
            token = user.verification_token

        response = client.get(f"/api/auth/verify/{token}")

        assert response.status_code == 200


class TestResendVerification:
    """Test resend verification email functionality."""

    def test_resend_verification_success(self, client, app):
        """Should be able to resend verification email."""
        client.post(
            "/api/auth/register",
            json={
                "email": "resend@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
        )

        response = client.post(
            "/api/auth/resend-verification", json={"email": "resend@example.com"}
        )

        assert response.status_code == 200
        assert "sent" in response.json["message"].lower()

    def test_resend_verification_already_verified(self, client, app, verified_user):
        """Should fail for already verified users."""
        response = client.post(
            "/api/auth/resend-verification", json={"email": verified_user["email"]}
        )

        assert response.status_code == 400
        assert "already verified" in response.json["error"].lower()

    def test_resend_verification_nonexistent_user(self, client):
        """Should not reveal if email exists (security)."""
        response = client.post(
            "/api/auth/resend-verification", json={"email": "nonexistent@example.com"}
        )

        assert response.status_code == 200

    def test_resend_verification_invalid_email(self, client):
        """Should fail with invalid email format."""
        response = client.post(
            "/api/auth/resend-verification", json={"email": "invalid-email"}
        )

        assert response.status_code == 400

    def test_resend_verification_missing_email(self, client):
        """Should fail when email is missing."""
        response = client.post("/api/auth/resend-verification", json={})

        assert response.status_code == 400


class TestPasswordReset:
    """Test password reset functionality."""

    def test_forgot_password_success(self, client, app, verified_user):
        """Should send password reset email."""
        response = client.post(
            "/api/auth/forgot-password", json={"email": verified_user["email"]}
        )

        assert response.status_code == 200
        assert "sent" in response.json["message"].lower()

    def test_forgot_password_nonexistent_user(self, client):
        """Should not reveal if email exists."""
        response = client.post(
            "/api/auth/forgot-password", json={"email": "nonexistent@example.com"}
        )

        assert response.status_code == 200

    def test_forgot_password_invalid_email(self, client):
        """Should fail with invalid email format."""
        response = client.post(
            "/api/auth/forgot-password", json={"email": "invalid-email"}
        )

        assert response.status_code == 400

    def test_forgot_password_missing_email(self, client):
        """Should fail when email is missing."""
        response = client.post("/api/auth/forgot-password", json={})

        assert response.status_code == 400

    def test_reset_password_success(self, client, app):
        """Should be able to reset password with valid token."""
        from app.views import generate_token

        client.post(
            "/api/auth/register",
            json={
                "email": "reset@example.com",
                "password": "OldPass123!",
                "confirm_password": "OldPass123!",
            },
        )

        with app.app_context():
            user = db.session.query(User).filter_by(email="reset@example.com").first()
            user.is_verified = True
            db.session.commit()
            user_id = user.user_id
            reset_token = generate_token(user_id, token_type="reset", expires_days=1)

        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "password": "NewPass456!",
                "confirm_password": "NewPass456!",
            },
        )

        assert response.status_code == 200
        assert "reset successfully" in response.json["message"].lower()

        # Verify new password works
        login_response = client.post(
            "/api/auth/login",
            json={"email": "reset@example.com", "password": "NewPass456!"},
        )
        assert login_response.status_code == 200

    def test_reset_password_invalid_token(self, client):
        """Should fail with invalid token."""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "invalid_token",
                "password": "NewPass456!",
                "confirm_password": "NewPass456!",
            },
        )

        assert response.status_code == 400

    def test_reset_password_weak_password(self, client, app, verified_user):
        """Should reject weak passwords in reset."""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": verified_user["token"],
                "password": "weak",
                "confirm_password": "weak",
            },
        )

        assert response.status_code == 400
        assert "password" in response.json.get("errors", {})

    def test_reset_password_mismatch(self, client, app, verified_user):
        """Should fail if passwords don't match."""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": verified_user["token"],
                "password": "NewPass456!",
                "confirm_password": "DifferentPass1!",
            },
        )

        assert response.status_code == 400

    def test_reset_password_missing_token(self, client):
        """Should fail when token is missing."""
        response = client.post(
            "/api/auth/reset-password",
            json={"password": "NewPass456!", "confirm_password": "NewPass456!"},
        )

        assert response.status_code == 400


class TestTokenRefresh:
    """Test token refresh functionality."""

    def test_refresh_token_success(self, client, app, verified_user):
        """Should be able to refresh token."""
        response = client.post(
            "/api/auth/refresh", json={"user_id": verified_user["user_id"]}
        )

        assert response.status_code == 200
        assert "token" in response.json
        assert "user" in response.json

    def test_refresh_token_invalid_user(self, client):
        """Should fail for non-existent user."""
        response = client.post("/api/auth/refresh", json={"user_id": 99999})

        assert response.status_code == 404

    def test_refresh_token_missing_user_id(self, client):
        """Should fail when user_id is missing."""
        response = client.post("/api/auth/refresh", json={})

        assert response.status_code == 400


class TestGetCurrentUser:
    """Test getting current user information."""

    def test_get_current_user_success(self, client, user_with_profile):
        """Should return current user data when authenticated."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert response.json["email"] == user_with_profile["email"]
        assert response.json["is_verified"]
        assert response.json["has_profile"]
        assert response.json["name"] == "Test User"

    def test_get_current_user_unauthenticated(self, client):
        """Should return 401 when not authenticated."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Should return 401 with invalid token."""
        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_get_current_user_malformed_header(self, client):
        """Should return 401 with malformed authorization header."""
        response = client.get(
            "/api/auth/me", headers={"Authorization": "InvalidFormat token"}
        )

        assert response.status_code == 401
