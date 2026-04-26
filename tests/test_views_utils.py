import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["MAILTRAP_SMTP_USER"] = None
    app.config["SECRET_KEY"] = "test-secret-key"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield


class TestValidatePasswordStrength:
    def test_password_too_short(self, app_context):
        from app.views import validate_password_strength

        result = validate_password_strength("Ab1!")
        assert not result["is_valid"]
        assert any("8 characters" in error for error in result["errors"])

    def test_password_no_uppercase(self, app_context):
        from app.views import validate_password_strength

        result = validate_password_strength("abcdefgh1!")
        assert not result["is_valid"]
        assert any("uppercase" in error.lower() for error in result["errors"])

    def test_password_no_lowercase(self, app_context):
        from app.views import validate_password_strength

        result = validate_password_strength("ABCDEFGH1!")
        assert not result["is_valid"]
        assert any("lowercase" in error.lower() for error in result["errors"])

    def test_password_no_number(self, app_context):
        from app.views import validate_password_strength

        result = validate_password_strength("Abcdefgh!!")
        assert not result["is_valid"]
        assert any("number" in error.lower() for error in result["errors"])

    def test_password_no_special(self, app_context):
        from app.views import validate_password_strength

        result = validate_password_strength("Abcdefgh123")
        assert not result["is_valid"]
        assert any("special" in error.lower() for error in result["errors"])

    def test_password_all_valid(self, app_context):
        from app.views import validate_password_strength

        result = validate_password_strength("TestPass123!")
        assert result["is_valid"]
        assert len(result["errors"]) == 0

    def test_password_multiple_errors(self, app_context):
        from app.views import validate_password_strength

        result = validate_password_strength("short")
        assert not result["is_valid"]
        assert len(result["errors"]) >= 3


class TestAllowedFile:
    def test_allowed_file_jpg(self, app_context):
        from app.views import allowed_file

        assert allowed_file("photo.jpg")

    def test_allowed_file_jpeg(self, app_context):
        from app.views import allowed_file

        assert allowed_file("photo.jpeg")

    def test_allowed_file_png(self, app_context):
        from app.views import allowed_file

        assert allowed_file("photo.png")

    def test_allowed_file_gif(self, app_context):
        from app.views import allowed_file

        assert allowed_file("photo.gif")

    def test_allowed_file_webp(self, app_context):
        from app.views import allowed_file

        assert allowed_file("photo.webp")

    def test_disallowed_file_exe(self, app_context):
        from app.views import allowed_file

        assert not allowed_file("malware.exe")

    def test_disallowed_file_pdf(self, app_context):
        from app.views import allowed_file

        assert not allowed_file("document.pdf")

    def test_disallowed_file_no_extension(self, app_context):
        from app.views import allowed_file

        assert not allowed_file("noextension")

    def test_disallowed_file_uppercase(self, app_context):
        from app.views import allowed_file

        assert allowed_file("photo.JPG")


class TestGenerateAndVerifyToken:
    def test_generate_token_returns_string(self, app_context):
        from app.views import generate_token

        token = generate_token(user_id=1)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self, app_context):
        from app.views import generate_token, verify_token

        token = generate_token(user_id=1)
        payload = verify_token(token)

        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["type"] == "auth"

    def test_verify_token_invalid(self, app_context):
        from app.views import verify_token

        payload = verify_token("invalid_token_string")
        assert payload is None

    def test_verify_token_wrong_type(self, app_context):
        from app.views import generate_token, verify_token

        token = generate_token(user_id=1, token_type="reset")
        payload = verify_token(token, token_type="auth")

        assert payload is None

    def test_generate_token_custom_type(self, app_context):
        from app.views import generate_token, verify_token

        token = generate_token(user_id=1, token_type="reset")
        payload = verify_token(token, token_type="reset")

        assert payload is not None
        assert payload["type"] == "reset"

    def test_generate_token_expired(self, app_context):
        from app.views import generate_token, verify_token

        token = generate_token(user_id=1, expires_days=0)
        payload = verify_token(token)
        assert payload is None


class TestSendEmail:
    def test_send_email_mock(self, app):
        with app.app_context():
            from app.views import send_email

            result = send_email(
                to_email="test@example.com",
                subject="Test Subject",
                body="<html><body>Test Body</body></html>",
            )

            assert result


class TestGetUserFromToken:
    def test_get_user_from_token_valid(self, client, app):
        from app import bcrypt

        with app.app_context():
            user = User(
                email="test@example.com",
                password_hash=bcrypt.generate_password_hash("TestPass123!").decode(
                    "utf-8"
                ),
                is_verified=True,
            )
            db.session.add(user)
            db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPass123!"},
        )
        token = login_response.json["token"]

        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_get_user_from_token_missing_header(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_user_from_token_invalid_format(self, client):
        response = client.get(
            "/api/auth/me", headers={"Authorization": "InvalidFormat token"}
        )
        assert response.status_code == 401

    def test_get_user_from_token_malformed_token(self, client):
        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer malformed_token"}
        )
        assert response.status_code == 401
