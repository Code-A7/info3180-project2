import os
import pytest
import tempfile
import shutil
from unittest.mock import patch

from app import create_app, db
from app.config import TestingConfig


class SocketEmitMock:
    """Mock for WebSocket emit function."""

    def __init__(self):
        self.emissions = []

    def __call__(self, user_id, event, data):
        self.emissions.append({"user_id": user_id, "event": event, "data": data})

    def clear(self):
        self.emissions = []

    def get_emissions_for_user(self, user_id):
        return [e for e in self.emissions if e["user_id"] == user_id]

    def get_emissions_by_event(self, event):
        return [e for e in self.emissions if e["event"] == event]


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    upload_dir = os.path.join(temp_dir, "uploads")

    class IsolatedTestingConfig(TestingConfig):
        SECRET_KEY = "test-secret-key-for-testing"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        SQLALCHEMY_ENGINE_OPTIONS = {}
        WTF_CSRF_ENABLED = False
        UPLOAD_FOLDER = upload_dir

    app = create_app(IsolatedTestingConfig)

    with app.app_context():
        from app import models  # noqa: F401

        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def clean_db(app):
    """Clean database before each test."""
    with app.app_context():
        # Delete data from all tables instead of dropping them
        # to speed up tests and avoid locks
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        db.session.remove()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def mock_socket_emit():
    """Create a mock for WebSocket emit function."""
    mock = SocketEmitMock()
    with patch("app.matches.set_socket_emit") as mock_set_emit:
        mock_set_emit.side_effect = lambda func: None
    with patch("app.matches.socket_emit", mock):
        yield mock


@pytest.fixture
def mock_socket_emit_direct():
    """Direct mock that patches socket_emit in matches module."""
    mock = SocketEmitMock()
    with patch("app.matches.socket_emit", mock):
        yield mock


@pytest.fixture
def verified_user(client, app):
    """Create a verified test user."""
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
        },
    )

    with app.app_context():
        from app.models import User

        user = db.session.query(User).filter_by(email="test@example.com").first()
        user.is_verified = True
        db.session.commit()
        user_id = user.user_id

    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )

    return {
        "user_id": user_id,
        "token": response.json["token"],
        "email": "test@example.com",
    }


@pytest.fixture
def user_with_profile(client, app, verified_user):
    """Create a verified user with a complete profile."""
    with app.app_context():
        from app.models import Profile

        profile = Profile(
            user_id=verified_user["user_id"],
            name="Test User",
            age=25,
            bio="Test bio for the user",
            gender="male",
            gender_preference="female",
            interests=["coding", "music", "reading", "gaming", "travel"],
            relationship_goal="serious_relationship",
            occupation="Developer",
            visibility=True,
        )
        db.session.add(profile)
        db.session.commit()

    return verified_user


@pytest.fixture
def second_user(client, app):
    """Create a second verified test user."""
    client.post(
        "/api/auth/register",
        json={
            "email": "second@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
        },
    )

    with app.app_context():
        from app.models import User

        user = db.session.query(User).filter_by(email="second@example.com").first()
        user.is_verified = True
        db.session.commit()
        user_id = user.user_id

    response = client.post(
        "/api/auth/login",
        json={"email": "second@example.com", "password": "TestPass123!"},
    )

    return {
        "user_id": user_id,
        "token": response.json["token"],
        "email": "second@example.com",
    }


@pytest.fixture
def second_user_with_profile(client, app, second_user):
    """Create a second verified user with a complete profile."""
    with app.app_context():
        from app.models import Profile

        profile = Profile(
            user_id=second_user["user_id"],
            name="Second User",
            age=28,
            bio="Profile for second test user",
            gender="female",
            gender_preference="male",
            interests=["cooking", "hiking", "yoga", "travel", "photography"],
            relationship_goal="serious_relationship",
            occupation="Designer",
            visibility=True,
        )
        db.session.add(profile)
        db.session.commit()

    return second_user


@pytest.fixture
def match_pair(client, app, user_with_profile, second_user_with_profile):
    """Create a mutual match between two users."""
    token1 = user_with_profile["token"]
    user2_id = second_user_with_profile["user_id"]
    user1_id = user_with_profile["user_id"]

    # Check if match already exists in database
    with app.app_context():
        from app.models import Match

        existing_match = Match.query.filter(
            ((Match.user1_id == user1_id) & (Match.user2_id == user2_id))
            | ((Match.user1_id == user2_id) & (Match.user2_id == user1_id))
        ).first()

        if existing_match:
            # Match already exists, just get the token for user2
            response = client.post(
                "/api/auth/login",
                json={"email": "second@example.com", "password": "TestPass123!"},
            )
            return {
                "user1": user_with_profile,
                "user2": second_user_with_profile,
                "token2": response.json["token"],
            }

    # User1 likes User2
    r1 = client.post(
        f"/api/matches/like/{user2_id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r1.status_code == 200, f"User1 like failed: {r1.json}"

    # Get fresh token for second user
    response = client.post(
        "/api/auth/login",
        json={"email": "second@example.com", "password": "TestPass123!"},
    )
    assert response.status_code == 200, f"Second user login failed: {response.json}"
    token2 = response.json["token"]

    # User2 likes User1 — this should create a mutual match
    r2 = client.post(
        f"/api/matches/like/{user1_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r2.status_code == 200, f"User2 like failed: {r2.json}"

    # Verify match was actually created
    with app.app_context():
        from app.models import Match

        match = Match.query.filter(
            ((Match.user1_id == user1_id) & (Match.user2_id == user2_id))
            | ((Match.user1_id == user2_id) & (Match.user2_id == user1_id))
        ).first()
        assert match is not None, "Match was not created after mutual likes"

    return {
        "user1": user_with_profile,
        "user2": second_user_with_profile,
        "token2": token2,
    }


@pytest.fixture
def third_user(client, app):
    """Create a third verified test user (for testing multiple users)."""
    client.post(
        "/api/auth/register",
        json={
            "email": "third@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
        },
    )

    with app.app_context():
        from app.models import User

        user = db.session.query(User).filter_by(email="third@example.com").first()
        user.is_verified = True
        db.session.commit()
        user_id = user.user_id

    response = client.post(
        "/api/auth/login",
        json={"email": "third@example.com", "password": "TestPass123!"},
    )

    return {
        "user_id": user_id,
        "token": response.json["token"],
        "email": "third@example.com",
    }


@pytest.fixture
def third_user_with_profile(client, app, third_user):
    """Create a third verified user with a complete profile."""
    with app.app_context():
        from app.models import Profile

        profile = Profile(
            user_id=third_user["user_id"],
            name="Third User",
            age=30,
            bio="Profile for third test user",
            gender="non_binary",
            gender_preference="all",
            interests=["art", "music", "writing", "theater", "reading"],
            relationship_goal="friendship",
            occupation="Artist",
            visibility=True,
        )
        db.session.add(profile)
        db.session.commit()

    return third_user


@pytest.fixture
def app_context(app):
    """Provide an app context for tests that need it."""
    with app.app_context():
        yield
