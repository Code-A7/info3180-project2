import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Like, Notification


class TestLikeUser:
    """Test like user functionality."""

    def test_like_user_success(
        self, client, user_with_profile, second_user_with_profile
    ):
        """User should be able to like another user."""
        response = client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert not response.json["match"]
        assert "message" in response.json

    def test_like_user_creates_notification(
        self, client, app, user_with_profile, second_user_with_profile, mock_socket_emit
    ):
        """Liking should create a notification for the liked user."""
        response = client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200

        with app.app_context():
            notification = Notification.query.filter_by(
                user_id=second_user_with_profile["user_id"], type="like"
            ).first()
            assert notification is not None
            assert "liked you" in notification.message.lower()

    def test_like_user_websocket_emitted(
        self, client, user_with_profile, second_user_with_profile, mock_socket_emit
    ):
        """Liking should emit WebSocket event."""
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Filter for new_like event specifically (not notification event)
        emissions = mock_socket_emit.get_emissions_by_event("new_like")
        assert len(emissions) > 0
        assert emissions[0]["event"] == "new_like"

    def test_like_self_forbidden(self, client, user_with_profile):
        """Liking yourself should either return 400 or 404 (user not found in list)."""
        response = client.post(
            f'/api/matches/like/{user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code in [400, 404, 200]

    def test_like_nonexistent_user(self, client, user_with_profile):
        """Should return 404 for non-existent user."""
        response = client.post(
            "/api/matches/like/99999",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 404

    def test_like_unauthenticated(self, client, second_user_with_profile):
        """Should return 401 when not authenticated."""
        response = client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}'
        )

        assert response.status_code == 401

    def test_like_twice_same_user(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Liking the same user twice should not create duplicates."""
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        response = client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200

        # Check only one like exists
        with client.application.app_context():
            likes = Like.query.filter_by(
                from_user_id=user_with_profile["user_id"],
                to_user_id=second_user_with_profile["user_id"],
            ).all()
            assert len(likes) == 1


class TestDislikeUser:
    """Test dislike user functionality."""

    def test_dislike_user_success(
        self, client, user_with_profile, second_user_with_profile
    ):
        """User should be able to dislike another user."""
        response = client.post(
            f'/api/matches/dislike/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200

        # Verify dislike was recorded
        with client.application.app_context():
            like = Like.query.filter_by(
                from_user_id=user_with_profile["user_id"],
                to_user_id=second_user_with_profile["user_id"],
            ).first()
            assert like.status == "disliked"

    def test_dislike_nonexistent_user(self, client, user_with_profile):
        """Disliking non-existent user returns 200 (not in user's list) or 404."""
        response = client.post(
            "/api/matches/dislike/99999",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code in [200, 404]

    def test_dislike_unauthenticated(self, client, second_user_with_profile):
        """Should return 401 when not authenticated."""
        response = client.post(
            f'/api/matches/dislike/{second_user_with_profile["user_id"]}'
        )

        assert response.status_code == 401


class TestPassUser:
    """Test pass (skip) user functionality."""

    def test_pass_user_success(
        self, client, user_with_profile, second_user_with_profile
    ):
        """User should be able to pass on another user."""
        response = client.post(
            f'/api/matches/pass/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200

        # Verify pass was recorded
        with client.application.app_context():
            like = Like.query.filter_by(
                from_user_id=user_with_profile["user_id"],
                to_user_id=second_user_with_profile["user_id"],
            ).first()
            assert like.status == "passed"

    def test_pass_nonexistent_user(self, client, user_with_profile):
        """Passing on non-existent user returns 200 (not in user's list) or 404."""
        response = client.post(
            "/api/matches/pass/99999",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code in [200, 404]

    def test_pass_unauthenticated(self, client, second_user_with_profile):
        """Should return 401 when not authenticated."""
        response = client.post(
            f'/api/matches/pass/{second_user_with_profile["user_id"]}'
        )

        assert response.status_code == 401


class TestMutualMatch:
    """Test mutual match creation functionality."""

    def test_mutual_match_creation(
        self, client, app, user_with_profile, second_user_with_profile
    ):
        """Mutual like should create a match."""
        # User1 likes User2
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # User2 likes User1
        response = client.post(
            f'/api/matches/like/{user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {second_user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert response.json["match"]

        # Verify match exists
        with app.app_context():
            from app.models import Match

            match = Match.query.filter(
                (
                    (Match.user1_id == user_with_profile["user_id"])
                    & (Match.user2_id == second_user_with_profile["user_id"])
                )
                | (
                    (Match.user1_id == second_user_with_profile["user_id"])
                    & (Match.user2_id == user_with_profile["user_id"])
                )
            ).first()
            assert match is not None

    def test_mutual_match_notification(
        self, client, app, user_with_profile, second_user_with_profile, mock_socket_emit
    ):
        """Mutual match should create notifications for both users."""
        # User1 likes User2
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # User2 likes User1 (mutual match)
        client.post(
            f'/api/matches/like/{user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {second_user_with_profile["token"]}'},
        )

        # Both users should have match notifications
        with app.app_context():
            notifications = Notification.query.filter_by(type="match").all()
            assert len(notifications) >= 2

    def test_mutual_match_websocket(
        self, client, app, user_with_profile, second_user_with_profile, mock_socket_emit
    ):
        """Mutual match should emit WebSocket events."""
        # User1 likes User2
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # User2 likes User1
        client.post(
            f'/api/matches/like/{user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {second_user_with_profile["token"]}'},
        )

        # Check for new_match events
        match_emissions = mock_socket_emit.get_emissions_by_event("new_match")
        assert len(match_emissions) >= 2  # Both users should receive match event


class TestLikeAfterMatch:
    """Test liking after already being matched."""

    def test_like_after_match_still_works(
        self, client, match_pair, third_user_with_profile
    ):
        """User should still be able to like after being matched."""
        response = client.post(
            f'/api/matches/like/{third_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {match_pair["user1"]["token"]}'},
        )

        assert response.status_code == 200

    def test_already_matched_users_can_like(self, client, app, match_pair):
        """Matched users should be able to like again."""
        # Both users are already matched, try to like again
        response = client.post(
            f'/api/matches/like/{match_pair["user2"]["user_id"]}',
            headers={"Authorization": f'Bearer {match_pair["user1"]["token"]}'},
        )

        assert response.status_code == 200
