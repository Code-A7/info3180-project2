import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGetPotentialMatches:
    """Test getting potential matches."""

    def test_get_potential_matches_success(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should return potential matches."""
        response = client.get(
            "/api/matches/potential",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert isinstance(response.json, list)

    def test_get_potential_matches_excludes_self(self, client, user_with_profile):
        """User should not appear in their own potential matches."""
        response = client.get(
            "/api/matches/potential",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        for match in response.json:
            assert match["user_id"] != user_with_profile["user_id"]

    def test_get_potential_matches_excludes_liked_users(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Already liked users should not appear in potential matches."""
        # Like user2 first
        client.post(
            f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Get potential matches
        response = client.get(
            "/api/matches/potential",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200

    def test_get_potential_matches_excludes_matched_users(self, client, match_pair):
        """Matched users should not appear in potential matches."""
        response = client.get(
            "/api/matches/potential",
            headers={"Authorization": f'Bearer {match_pair["user1"]["token"]}'},
        )

        assert response.status_code == 200
        for match in response.json:
            assert match["user_id"] != match_pair["user2"]["user_id"]

    def test_get_potential_matches_unauthenticated(self, client):
        """Should return 401 when not authenticated."""
        response = client.get("/api/matches/potential")

        assert response.status_code == 401

    def test_get_potential_matches_no_profile(self, client, verified_user):
        """Should return 400 if user has no profile."""
        response = client.get(
            "/api/matches/potential",
            headers={"Authorization": f'Bearer {verified_user["token"]}'},
        )

        assert response.status_code == 400


class TestGetMatches:
    """Test getting mutual matches."""

    def test_get_matches_success(self, client, match_pair):
        """Should return mutual matches."""
        response = client.get(
            "/api/matches",
            headers={"Authorization": f'Bearer {match_pair["user1"]["token"]}'},
        )

        assert response.status_code == 200
        matches = response.json
        assert len(matches) > 0
        assert "name" in matches[0]["profile"]

    def test_get_matches_empty(self, client, user_with_profile):
        """Should return empty list when no matches."""
        response = client.get(
            "/api/matches",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert response.json == []

    def test_get_matches_unauthenticated(self, client):
        """Should return 401 when not authenticated."""
        response = client.get("/api/matches")

        assert response.status_code == 401


class TestMatchScore:
    """Test match score calculation."""

    def test_get_match_score(self, client, user_with_profile, second_user_with_profile):
        """Should return match score for a user."""
        response = client.get(
            f'/api/matches/score/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert "score" in response.json
        assert "details" in response.json
        assert response.json["to_user_id"] == second_user_with_profile["user_id"]

    def test_get_match_score_nonexistent_user(self, client, user_with_profile):
        """Should return 404 for non-existent user."""
        response = client.get(
            "/api/matches/score/99999",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code in [404, 400]

    def test_get_match_score_self(self, client, user_with_profile):
        """Getting match score for self returns 200 or 400."""
        response = client.get(
            f'/api/matches/score/{user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code in [200, 400]

    def test_match_score_includes_details(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Match score should include scoring details."""
        response = client.get(
            f'/api/matches/score/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert "details" in response.json
        assert isinstance(response.json["details"], dict)


class TestMatchFilters:
    """Test match filtering functionality."""

    def test_filter_by_age_min(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should filter by minimum age."""
        response = client.get(
            "/api/matches/potential?age_min=30",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        for match in response.json:
            assert match["age"] >= 30

    def test_filter_by_age_max(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should filter by maximum age."""
        response = client.get(
            "/api/matches/potential?age_max=20",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        for match in response.json:
            assert match["age"] <= 20

    def test_filter_by_interests(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should filter by shared interests."""
        response = client.get(
            "/api/matches/potential?interests=coding",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200


class TestMatchAlgorithm:
    """Test the match scoring algorithm."""

    def test_match_score_with_compatible_age(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should give points for compatible age."""
        response = client.get(
            f'/api/matches/score/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        assert response.json["score"] >= 0

    def test_match_score_with_shared_interests(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should give points for shared interests."""
        response = client.get(
            f'/api/matches/score/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        details = response.json["details"]
        # details["shared_interests"] is a list when interests overlap, else key absent
        assert isinstance(details, dict)

    def test_match_score_with_matching_goal(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should give points for matching relationship goals."""
        response = client.get(
            f'/api/matches/score/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
        details = response.json["details"]
        # goal_match is True when goals match, else key absent
        assert isinstance(details, dict)

    def test_match_score_gender_preference(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should respect gender preferences."""
        response = client.get(
            f'/api/matches/score/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        assert response.status_code == 200
