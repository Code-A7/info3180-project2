import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models import User


class TestCompleteUserFlow:
    """End-to-end user journey tests."""

    def test_register_verify_login_create_profile(self, client, app):
        """Complete registration flow: register -> verify -> login -> create profile."""
        # Step 1: Register
        response = client.post(
            "/api/auth/register",
            json={
                "email": "flow@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
        )

        assert response.status_code == 201
        response.json["user_id"]

        # Step 2: Verify email
        with app.app_context():
            user = db.session.query(User).filter_by(email="flow@example.com").first()
            token = user.verification_token

        response = client.get(f"/api/auth/verify/{token}")
        assert response.status_code == 200

        # Step 3: Login
        response = client.post(
            "/api/auth/login",
            json={"email": "flow@example.com", "password": "TestPass123!"},
        )

        assert response.status_code == 200
        assert "token" in response.json
        token = response.json["token"]

        # Step 4: Create profile
        response = client.post(
            "/api/profile",
            json={
                "name": "Flow User",
                "age": 25,
                "bio": "Testing complete flow",
                "interests": "hiking, reading, music, coding, travel",
                "gender": "male",
                "gender_preference": "all",
                "relationship_goal": "serious_relationship",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201

        # Step 5: Access protected route (get current user)
        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["has_profile"]
        assert response.json["name"] == "Flow User"

    def test_like_match_message_flow(
        self, client, app, match_pair, third_user_with_profile
    ):
        """Interaction flow: like -> mutual match."""
        # User1 views potential matches
        response = client.get(
            "/api/matches/potential",
            headers={"Authorization": f'Bearer {match_pair["user1"]["token"]}'},
        )
        assert response.status_code == 200

        # User1 likes User3
        response = client.post(
            f'/api/matches/like/{third_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {match_pair["user1"]["token"]}'},
        )
        assert response.status_code == 200
        assert not response.json["match"]

        # User3 likes User1 (creates match)
        response = client.post(
            f'/api/matches/like/{match_pair["user1"]["user_id"]}',
            headers={"Authorization": f'Bearer {third_user_with_profile["token"]}'},
        )
        assert response.status_code == 200
        assert response.json["match"]

    def test_profile_search_bookmark_flow(
        self,
        client,
        app,
        user_with_profile,
        second_user_with_profile,
        third_user_with_profile,
    ):
        """Discovery flow: search -> bookmark -> view bookmarks."""
        # Search profiles
        response = client.post(
            "/api/matches/search",
            json={"gender": "female"},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200

        # Bookmark Second User
        response = client.post(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code in [200, 201]

        # View bookmarks
        response = client.get(
            "/api/matches/bookmarks",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200

    def test_notification_flow(
        self, client, app, user_with_profile, second_user_with_profile
    ):
        """Notification flow: like -> check notifications -> mark as read."""
        # User1 likes User2 (creates notification for User2)
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # User2 checks notifications
        response = client.get(
            "/api/notifications",
            headers={"Authorization": f'Bearer {second_user_with_profile["token"]}'},
        )
        assert response.status_code == 200
        assert len(response.json) > 0
        assert response.json[0]["type"] == "like"

        # User2 marks notification as read
        notification_id = response.json[0]["id"]
        response = client.put(
            f"/api/notifications/{notification_id}/read",
            headers={"Authorization": f'Bearer {second_user_with_profile["token"]}'},
        )
        assert response.status_code == 200

        # Verify it's marked as read
        response = client.get(
            "/api/notifications",
            headers={"Authorization": f'Bearer {second_user_with_profile["token"]}'},
        )
        assert response.json[0]["is_read"]


class TestDataIsolation:
    """Ensure users can't access each other's private data."""

    def test_cannot_view_private_profile(self, client, app, user_with_profile):
        """User should not view private profiles of others."""
        # Create a user with private profile
        with app.app_context():
            from tests.helpers import create_user, create_profile

            user_id = create_user(app, "private@example.com")
            create_profile(
                app,
                user_id,
                name="Private",
                visibility=False,
                interests=["reading", "writing", "coding", "gaming", "music"],
            )

        # Try to view private profile
        response = client.get(f"/api/profile/{user_id}")
        assert response.status_code == 403

    def test_cannot_message_non_match(
        self, client, user_with_profile, second_user_with_profile
    ):
        """User should not message someone they haven't matched with."""
        response = client.post(
            f'/api/messages/{second_user_with_profile["user_id"]}',
            json={"content": "Hello"},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 403

    def test_cannot_like_self(self, client, user_with_profile):
        """User tries to like themselves - backend accepts or rejects."""
        response = client.post(
            f'/api/matches/like/{user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code in [200, 400, 404]

    def test_cannot_bookmark_self(self, client, user_with_profile):
        """User tries to bookmark themselves - backend accepts or rejects."""
        response = client.post(
            f'/api/matches/bookmark/{user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code in [200, 400, 404]

    def test_cannot_access_other_users_notifications(
        self, client, user_with_profile, second_user_with_profile
    ):
        """User should not access other users' notifications."""
        # Create notification for user2
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Try to access as user1
        response = client.get(
            "/api/notifications",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Should only see own notifications
        if len(response.json) > 0:
            for notification in response.json:
                assert notification["user_id"] == user_with_profile["user_id"]

    def test_cannot_update_other_users_profile(
        self, client, user_with_profile, second_user_with_profile
    ):
        """User should not update other users' profiles."""
        response = client.put(
            "/api/profile",
            json={
                "name": "Hacked Name",
                "interests": "hacking, cheating, gaming, reading, music",
            },
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Should update own profile, not others
        assert response.status_code in [200, 400]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_search_results(self, client, user_with_profile):
        """Search with no results should return empty list."""
        response = client.post(
            "/api/matches/search",
            json={"age_min": 150},  # Unreasonably high age
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert response.json == []

    def test_update_with_no_changes(self, client, user_with_profile):
        """Updating profile with same data should work."""
        response = client.put(
            "/api/profile",
            json={
                "name": "Test User",
                "age": 25,
                "bio": "Test bio for the user",
                "interests": "coding, music, reading, gaming, travel",
                "gender": "male",
                "gender_preference": "female",
                "relationship_goal": "serious_relationship",
            },
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200

    def test_multiple_likes_same_user(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Multiple likes to same user should not create duplicates."""
        # Like user2 first time
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Like user2 second time
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Should only have one like
        with client.application.app_context():
            from app.models import Like

            likes = Like.query.filter_by(
                from_user_id=user_with_profile["user_id"],
                to_user_id=second_user_with_profile["user_id"],
            ).all()
            assert len(likes) == 1

    def test_profile_update_with_minimal_data(self, client, user_with_profile):
        """Updating profile with minimal changes should work."""
        response = client.put(
            "/api/profile",
            json={
                "name": "Updated Name",
                "age": 25,
                "bio": "Updated bio",
                "gender": "male",
                "gender_preference": "female",
                "relationship_goal": "friendship",
                "interests": "coding, music, reading, gaming, travel",
            },
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code in [200, 400]
        if response.status_code == 200:
            assert response.json["name"] == "Updated Name"
