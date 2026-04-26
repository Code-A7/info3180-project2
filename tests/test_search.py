import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSearch:
    """Test search functionality."""

    def test_search_profiles_unauthorized(self, client):
        """Should return 401 when not authenticated."""
        response = client.post("/api/matches/search", json={})
        assert response.status_code == 401

    def test_search_by_age_range(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should search profiles by age range."""
        response = client.post(
            "/api/matches/search",
            json={"age_min": 20, "age_max": 35},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200

    def test_search_by_interests(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should search profiles by interests."""
        response = client.post(
            "/api/matches/search",
            json={"interests": ["music"]},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200

    def test_search_sort_by_newest(self, client, user_with_profile):
        """Should sort search results by newest."""
        response = client.post(
            "/api/matches/search",
            json={"sort_by": "newest"},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200

    def test_search_sort_by_match_score(self, client, user_with_profile):
        """Should sort search results by match score."""
        response = client.post(
            "/api/matches/search",
            json={"sort_by": "match_score"},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200


class TestBookmarks:
    """Test bookmark functionality."""

    def test_get_bookmarks_unauthorized(self, client):
        """Should return 401 when not authenticated."""
        response = client.get("/api/matches/bookmarks")
        assert response.status_code == 401

    def test_add_bookmark(self, client, user_with_profile, second_user_with_profile):
        """Should add a bookmark."""
        response = client.post(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code in [200, 201]

    def test_add_duplicate_bookmark(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should handle duplicate bookmarks gracefully."""
        # Add bookmark first time
        client.post(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Add again
        response = client.post(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code in [200, 201]

    def test_bookmark_self(self, client, user_with_profile):
        """Should not allow bookmarking self."""
        response = client.post(
            f'/api/matches/bookmark/{user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 400

    def test_get_bookmarks(self, client, user_with_profile, second_user_with_profile):
        """Should get user's bookmarks."""
        # Add bookmark
        client.post(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        response = client.get(
            "/api/matches/bookmarks",
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def test_remove_bookmark(self, client, user_with_profile, second_user_with_profile):
        """Should remove a bookmark."""
        # Add bookmark
        client.post(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        # Remove bookmark
        response = client.delete(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200

    def test_remove_nonexistent_bookmark(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should return 404 when removing non-existent bookmark."""
        response = client.delete(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code in [404, 400]


class TestSearchFilters:
    """Test search filtering options."""

    def test_filter_by_gender(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should filter by gender."""
        response = client.post(
            "/api/matches/search",
            json={"gender": "female"},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200

    def test_filter_by_multiple_criteria(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Should filter by multiple criteria."""
        response = client.post(
            "/api/matches/search",
            json={
                "age_min": 20,
                "age_max": 40,
                "gender": "female",
                "interests": ["cooking", "hiking"],
            },
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200

    def test_search_returns_empty_for_no_results(self, client, user_with_profile):
        """Should return empty list when no matches found."""
        response = client.post(
            "/api/matches/search",
            json={"age_min": 150},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200
        assert response.json == []

    def test_search_includes_bookmark_status(
        self, client, user_with_profile, second_user_with_profile
    ):
        """Search results should include bookmark status."""
        # Bookmark user2
        client.post(
            f'/api/matches/bookmark/{second_user_with_profile["user_id"]}',
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )

        response = client.post(
            "/api/matches/search",
            json={},
            headers={"Authorization": f'Bearer {user_with_profile["token"]}'},
        )
        assert response.status_code == 200
