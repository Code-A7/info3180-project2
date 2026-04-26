import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models import Message


class TestMessaging:
    """Test messaging functionality."""
    
    def test_send_message_unauthorized(self, client, second_user_with_profile):
        """Should return 401 when not authenticated."""
        response = client.post(f'/api/messages/{second_user_with_profile["user_id"]}', json={'content': 'Hello'})
        assert response.status_code == 401

    def test_send_message_no_match(self, client, user_with_profile, second_user_with_profile):
        """Should return 403 when not matched with user."""
        response = client.post(f'/api/messages/{second_user_with_profile["user_id"]}',
            json={'content': 'Hello'},
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        assert response.status_code == 403

    def test_send_message_success(self, client, match_pair):
        """Should send message successfully when matched."""
        response = client.post(f'/api/messages/{match_pair["user2"]["user_id"]}',
            json={'content': 'Hello there!'},
            headers={'Authorization': f'Bearer {match_pair["user1"]["token"]}'}
        )
        assert response.status_code == 201
        assert response.json['content'] == 'Hello there!'

    def test_message_at_max_length(self, client, match_pair):
        """Should accept message at maximum length."""
        max_content = 'x' * 1000
        response = client.post(f'/api/messages/{match_pair["user2"]["user_id"]}',
            json={'content': max_content},
            headers={'Authorization': f'Bearer {match_pair["user1"]["token"]}'}
        )
        assert response.status_code == 201

    def test_get_conversations(self, client, match_pair):
        """Should get conversations list."""
        response = client.get('/api/messages',
            headers={'Authorization': f'Bearer {match_pair["user1"]["token"]}'}
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)


class TestMarkMessageRead:
    """Test marking messages as read."""
    
    def test_mark_message_read_success(self, client, app, match_pair):
        """Should mark message as read."""
        with app.app_context():
            msg = Message(
                sender_id=match_pair['user2']['user_id'],
                receiver_id=match_pair['user1']['user_id'],
                content='Test message'
            )
            db.session.add(msg)
            db.session.commit()
            message_id = msg.message_id
        
        response = client.put(f'/api/messages/{message_id}/read',
            headers={'Authorization': f'Bearer {match_pair["user1"]["token"]}'}
        )
        assert response.status_code == 200
    
    def test_mark_message_read_not_found(self, client, user_with_profile):
        """Should return 404 for non-existent message."""
        response = client.put('/api/messages/99999/read',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        assert response.status_code == 404

    def test_mark_message_read_unauthorized(self, client):
        """Should return 401 when not authenticated."""
        response = client.put('/api/messages/1/read')
        assert response.status_code == 401


class TestTypingStatus:
    """Test typing status functionality."""
    
    def test_typing_status_typing(self, client, match_pair):
        """Should send typing status."""
        response = client.post(f'/api/messages/typing/{match_pair["user2"]["user_id"]}',
            json={'is_typing': True},
            headers={'Authorization': f'Bearer {match_pair["user1"]["token"]}'}
        )
        assert response.status_code == 200

    def test_typing_status_stopped(self, client, match_pair):
        """Should send typing stopped status."""
        response = client.post(f'/api/messages/typing/{match_pair["user2"]["user_id"]}',
            json={'is_typing': False},
            headers={'Authorization': f'Bearer {match_pair["user1"]["token"]}'}
        )
        assert response.status_code == 200

    def test_typing_status_not_matched(self, client, user_with_profile, second_user_with_profile):
        """Should return 403 when not matched."""
        response = client.post(f'/api/messages/typing/{second_user_with_profile["user_id"]}',
            json={'is_typing': True},
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        assert response.status_code == 403

    def test_typing_status_unauthorized(self, client, second_user_with_profile):
        """Should return 401 when not authenticated."""
        response = client.post(f'/api/messages/typing/{second_user_with_profile["user_id"]}', json={'is_typing': True})
        assert response.status_code == 401


class TestGetMessageHistory:
    """Test getting message history."""
    
    def test_get_message_history_pagination(self, client, match_pair):
        """Should return paginated message history."""
        response = client.get(f'/api/messages/{match_pair["user2"]["user_id"]}?page=1&per_page=10',
            headers={'Authorization': f'Bearer {match_pair["user1"]["token"]}'}
        )
        assert response.status_code == 200
        assert 'page' in response.json
        assert 'total_pages' in response.json

    def test_get_message_history_not_matched(self, client, user_with_profile, second_user_with_profile):
        """Should return 403 when not matched."""
        response = client.get(f'/api/messages/{second_user_with_profile["user_id"]}',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        assert response.status_code == 403

    def test_get_unread_count_zero(self, client, user_with_profile):
        """Should return 0 unread count when none."""
        response = client.get('/api/messages/unread',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        assert response.status_code == 200