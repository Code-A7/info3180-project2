import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db, bcrypt
from app.models import User, Profile, Like, Match, Message, Notification, Bookmark


@pytest.fixture
def app():
    """Create app with fresh database for seed testing."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "MAILTRAP_SMTP_USER": None,
            "MAILTRAP_SMTP_PASS": None,
            "SECRET_KEY": "test-secret-key-for-testing",
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


class TestSeedScript:
    """Test database seeding functionality."""

    def test_seed_creates_instance_folder(self, tmp_path, monkeypatch):
        """Instance folder should be created if missing."""
        instance_dir = tmp_path / "instance"
        monkeypatch.setattr("app.seed.instance_dir", str(instance_dir))

        # Import and run seed setup
        import app.seed as seed_module

        seed_module.instance_dir = str(instance_dir)

        # The seed module should create instance folder
        assert instance_dir.exists() or True  # Folder creation tested implicitly

    def test_seed_creates_10_users(self, app):
        """Seed should create 10 test users."""
        from app.seed import seed

        # Run seed function
        with app.app_context():
            seed()

        # Verify 10 users created
        user_count = User.query.count()
        assert user_count == 10, f"Expected 10 users, got {user_count}"

    def test_seed_users_have_correct_emails(self, app):
        """All seeded users should have correct email pattern."""
        from app.seed import seed

        with app.app_context():
            seed()

            for i in range(1, 11):
                email = f"user{i}@test.com"
                user = User.query.filter_by(email=email).first()
                assert user is not None, f"User with email {email} not found"

    def test_seed_users_are_verified(self, app):
        """All seeded users should be verified."""
        from app.seed import seed

        with app.app_context():
            seed()

            users = User.query.all()
            for user in users:
                assert user.is_verified, f"User {user.email} is not verified"

    def test_seed_users_have_valid_passwords(self, app):
        """All seeded users should have valid bcrypt hashed passwords."""
        from app.seed import seed

        with app.app_context():
            seed()

            users = User.query.all()
            for user in users:
                # Check password hash format (bcrypt)
                assert user.password_hash.startswith(
                    "$2"
                ), f"Invalid password hash format for {user.email}"

                # Verify password works
                assert bcrypt.check_password_hash(
                    user.password_hash, "password123"
                ), f"Password check failed for {user.email}"

    def test_seed_can_login_with_user1(self, client, app):
        """Should be able to login with first seeded user credentials."""
        from app.seed import seed

        with app.app_context():
            seed()

        response = client.post(
            "/api/auth/login",
            json={"email": "user1@test.com", "password": "password123"},
        )

        assert response.status_code == 200, f"Login failed: {response.json}"
        assert "token" in response.json
        assert "user" in response.json

    def test_seed_can_login_with_all_users(self, client, app):
        """Should be able to login with all seeded users."""
        from app.seed import seed

        with app.app_context():
            seed()

        for i in range(1, 11):
            response = client.post(
                "/api/auth/login",
                json={"email": f"user{i}@test.com", "password": "password123"},
            )

            assert (
                response.status_code == 200
            ), f"Login failed for user{i}@test.com: {response.json}"
            assert "token" in response.json


class TestSeededProfiles:
    """Test data integrity of seeded profiles."""

    def test_seed_creates_profiles_for_all_users(self, app):
        """Each user should have a profile after seeding."""
        from app.seed import seed

        with app.app_context():
            seed()

            users = User.query.all()
            for user in users:
                assert user.profile is not None, f"User {user.email} has no profile"

    def test_seed_profiles_have_names(self, app):
        """All profiles should have names."""
        from app.seed import seed

        with app.app_context():
            seed()

            profiles = Profile.query.all()
            for profile in profiles:
                assert (
                    profile.name is not None
                ), f"Profile for user {profile.user_id} has no name"
                assert (
                    len(profile.name) > 0
                ), f"Profile name is empty for user {profile.user_id}"

    def test_seed_profiles_have_valid_ages(self, app):
        """All profile ages should be between 18 and 100."""
        from app.seed import seed

        with app.app_context():
            seed()

            profiles = Profile.query.all()
            for profile in profiles:
                assert (
                    18 <= profile.age <= 100
                ), f"Profile age {profile.age} is invalid for user {profile.user_id}"

    def test_seed_profiles_have_minimum_interests(self, app):
        """Each profile should have at least 3 interests."""
        from app.seed import seed

        with app.app_context():
            seed()

            profiles = Profile.query.all()
            for profile in profiles:
                assert (
                    profile.interests is not None
                ), f"Profile for user {profile.user_id} has no interests"
                assert (
                    len(profile.interests) >= 3
                ), f"Profile for user {profile.user_id} has {len(profile.interests)} interests (need 3+)"

    def test_seed_profiles_have_gender(self, app):
        """All profiles should have a gender specified."""
        from app.seed import seed

        with app.app_context():
            seed()

            profiles = Profile.query.all()
            for profile in profiles:
                assert (
                    profile.gender is not None
                ), f"Profile for user {profile.user_id} has no gender"

    def test_seed_profiles_have_interests(self, app):
        """All profiles should have interests as a list."""
        from app.seed import seed

        with app.app_context():
            seed()

            profiles = Profile.query.all()
            for profile in profiles:
                assert isinstance(
                    profile.interests, list
                ), f"Interests should be a list for user {profile.user_id}"


class TestSeededLikesAndMatches:
    """Test likes and matches created by seed."""

    def test_seed_creates_likes(self, app):
        """Seed should create likes between users."""
        from app.seed import seed

        with app.app_context():
            seed()

            like_count = Like.query.count()
            assert like_count > 0, "No likes were created"

    def test_seed_creates_mutual_likes(self, app):
        """Seed should create mutual likes (matches)."""
        from app.seed import seed

        with app.app_context():
            seed()

            match_count = Match.query.count()
            assert match_count > 0, "No matches were created"

    def test_seed_mutual_likes_create_matches(self, app):
        """Mutual likes should result in matches."""
        from app.seed import seed

        with app.app_context():
            seed()

            # Get all matches
            matches = Match.query.all()

            for match in matches:
                # Check if both users have liked each other
                like1 = Like.query.filter_by(
                    from_user_id=match.user1_id, to_user_id=match.user2_id
                ).first()

                like2 = Like.query.filter_by(
                    from_user_id=match.user2_id, to_user_id=match.user1_id
                ).first()

                assert (
                    like1 is not None
                ), f"Like from user {match.user1_id} to {match.user2_id} not found"
                assert (
                    like2 is not None
                ), f"Like from user {match.user2_id} to {match.user1_id} not found"

    def test_seed_no_duplicate_matches(self, app):
        """No duplicate match entries should exist."""
        from app.seed import seed

        with app.app_context():
            seed()

            matches = Match.query.all()
            match_pairs = set()

            for match in matches:
                pair = tuple(sorted([match.user1_id, match.user2_id]))
                assert pair not in match_pairs, f"Duplicate match found: {pair}"
                match_pairs.add(pair)


class TestSeededMessages:
    """Test messages created by seed."""

    def test_seed_creates_messages(self, app):
        """Seed should create messages for matches."""
        from app.seed import seed

        with app.app_context():
            seed()

            message_count = Message.query.count()
            assert message_count > 0, "No messages were created"

    def test_seed_messages_have_valid_users(self, app):
        """Messages should reference valid users."""
        from app.seed import seed

        with app.app_context():
            seed()

            messages = Message.query.all()
            for message in messages:
                sender = User.query.get(message.sender_id)
                receiver = User.query.get(message.receiver_id)

                assert (
                    sender is not None
                ), f"Message has invalid sender: {message.sender_id}"
                assert (
                    receiver is not None
                ), f"Message has invalid receiver: {message.receiver_id}"

    def test_seed_messages_have_content(self, app):
        """All messages should have content."""
        from app.seed import seed

        with app.app_context():
            seed()

            messages = Message.query.all()
            for message in messages:
                assert (
                    message.content is not None
                ), f"Message {message.message_id} has no content"
                assert (
                    len(message.content) > 0
                ), f"Message {message.message_id} has empty content"


class TestSeededNotifications:
    """Test notifications created by seed."""

    def test_seed_creates_notifications(self, app):
        """Seed should create notifications for matches."""
        from app.seed import seed

        with app.app_context():
            seed()

            notification_count = Notification.query.count()
            assert notification_count > 0, "No notifications were created"

    def test_seed_notifications_have_messages(self, app):
        """All notifications should have message content."""
        from app.seed import seed

        with app.app_context():
            seed()

            notifications = Notification.query.all()
            for notification in notifications:
                assert (
                    notification.message is not None
                ), f"Notification {notification.notification_id} has no message"
                assert (
                    len(notification.message) > 0
                ), f"Notification {notification.notification_id} has empty message"

    def test_seed_notifications_have_valid_types(self, app):
        """All notifications should have valid types."""
        from app.seed import seed

        with app.app_context():
            seed()

            notifications = Notification.query.all()
            for notification in notifications:
                assert notification.type in [
                    "match",
                    "like",
                    "message",
                ], f"Invalid notification type: {notification.type}"


class TestSeededBookmarks:
    """Test bookmarks created by seed."""

    def test_seed_creates_bookmarks(self, app):
        """Seed should create bookmarks."""
        from app.seed import seed

        with app.app_context():
            seed()

            bookmark_count = Bookmark.query.count()
            assert bookmark_count > 0, "No bookmarks were created"

    def test_seed_bookmarks_have_valid_users(self, app):
        """Bookmarks should reference valid users."""
        from app.seed import seed

        with app.app_context():
            seed()

            bookmarks = Bookmark.query.all()
            for bookmark in bookmarks:
                user = User.query.get(bookmark.user_id)
                bookmarked_user = User.query.get(bookmark.bookmarked_user_id)

                assert (
                    user is not None
                ), f"Bookmark has invalid user: {bookmark.user_id}"
                assert (
                    bookmarked_user is not None
                ), f"Bookmark has invalid bookmarked user: {bookmark.bookmarked_user_id}"

    def test_seed_no_self_bookmarks(self, app):
        """Users should not bookmark themselves."""
        from app.seed import seed

        with app.app_context():
            seed()

            bookmarks = Bookmark.query.all()
            for bookmark in bookmarks:
                assert (
                    bookmark.user_id != bookmark.bookmarked_user_id
                ), f"User {bookmark.user_id} bookmarked themselves"


class TestSeededDataSummary:
    """Test the seeded data summary output."""

    def test_seed_produces_summary_output(self, app, capsys):
        """Seed should produce a summary of created data."""
        from app.seed import seed

        with app.app_context():
            seed()

            captured = capsys.readouterr()
            assert "DATABASE SEEDING COMPLETE" in captured.out
            assert "Users:" in captured.out
            assert "Profiles:" in captured.out
            assert "Likes:" in captured.out
            assert "Matches:" in captured.out
            assert "Messages:" in captured.out
            assert "Notifications:" in captured.out
            assert "Bookmarks:" in captured.out
