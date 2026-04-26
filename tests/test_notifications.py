import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Notification


class TestGetNotifications:
    """Test getting notifications."""
    
    def test_get_notifications_success(self, client, match_pair):
        """Should return notifications for user."""
        response = client.get('/api/notifications',
            headers={'Authorization': f'Bearer {match_pair["user2"]["token"]}'}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
    
    def test_get_notifications_unauthenticated(self, client):
        """Should return 401 when not authenticated."""
        response = client.get('/api/notifications')
        
        assert response.status_code == 401
    
    def test_get_notifications_empty(self, client, user_with_profile):
        """Should return empty list when no notifications."""
        response = client.get('/api/notifications',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
        assert response.json == []


class TestNotificationCreation:
    """Test notification creation."""
    
    def test_like_creates_notification(self, client, app, user_with_profile, second_user_with_profile):
        """Liking a user should create a notification."""
        client.post(f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        with app.app_context():
            notification = Notification.query.filter_by(
                user_id=second_user_with_profile['user_id'],
                type='like'
            ).first()
            assert notification is not None
    
    def test_match_creates_notification(self, client, app, user_with_profile, second_user_with_profile):
        """Mutual match should create notifications."""
        # User1 likes User2
        client.post(f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        # User2 likes User1 (creates match)
        client.post(f'/api/matches/like/{user_with_profile["user_id"]}',
            headers={'Authorization': f'Bearer {second_user_with_profile["token"]}'}
        )
        
        # Both users should have match notifications
        with app.app_context():
            notifications = Notification.query.filter_by(type='match').all()
            assert len(notifications) >= 2


class TestMarkNotificationRead:
    """Test marking notifications as read."""
    
    def test_mark_notification_as_read(self, client, app, match_pair):
        """Should mark notification as read."""
        # Get notification ID
        response = client.get('/api/notifications',
            headers={'Authorization': f'Bearer {match_pair["user2"]["token"]}'}
        )
        
        if len(response.json) > 0:
            notification_id = response.json[0]['id']
            
            # Mark as read
            response = client.put(f'/api/notifications/{notification_id}/read',
                headers={'Authorization': f'Bearer {match_pair["user2"]["token"]}'}
            )
            
            assert response.status_code == 200
            
            # Verify it's marked
            response = client.get('/api/notifications',
                headers={'Authorization': f'Bearer {match_pair["user2"]["token"]}'}
            )
            assert response.json[0]['is_read'] == True
    
    def test_mark_notification_read_not_found(self, client, user_with_profile):
        """Should return 404 for non-existent notification."""
        response = client.put('/api/notifications/99999/read',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        assert response.status_code == 404
    
    def test_mark_notification_read_unauthorized(self, client, app, user_with_profile, second_user_with_profile):
        """User should not be able to mark another user's notification."""
        # Create a notification for user2
        client.post(f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        # Try to mark as read as user2
        with app.app_context():
            notification = Notification.query.filter_by(
                user_id=second_user_with_profile['user_id']
            ).first()
            if notification:
                response = client.put(f'/api/notifications/{notification.notification_id}/read',
                    headers={'Authorization': f'Bearer {second_user_with_profile["token"]}'}
                )
                assert response.status_code == 200


class TestMarkAllNotificationsRead:
    """Test marking all notifications as read."""
    
    def test_mark_all_as_read(self, client, app, user_with_profile, second_user_with_profile):
        """Should mark all notifications as read."""
        # Create multiple notifications
        client.post(f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        response = client.put('/api/notifications/read-all',
            headers={'Authorization': f'Bearer {second_user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
        
        # Verify all marked
        response = client.get('/api/notifications/unread-count',
            headers={'Authorization': f'Bearer {second_user_with_profile["token"]}'}
        )
        assert response.json['unread_count'] == 0


class TestUnreadNotificationCount:
    """Test getting unread notification count."""
    
    def test_get_unread_count(self, client, app, user_with_profile, second_user_with_profile):
        """Should return unread notification count."""
        # Create notification
        client.post(f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        response = client.get('/api/notifications/unread-count',
            headers={'Authorization': f'Bearer {second_user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
        assert response.json['unread_count'] >= 1
    
    def test_get_unread_count_zero(self, client, user_with_profile):
        """Should return 0 when no unread notifications."""
        response = client.get('/api/notifications/unread-count',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
        assert response.json['unread_count'] == 0


class TestNotificationData:
    """Test notification data structure."""
    
    def test_notification_includes_sender_profile(self, client, app, user_with_profile, second_user_with_profile):
        """Notification should include sender's profile data."""
        client.post(f'/api/matches/like/{second_user_with_profile["user_id"]}',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        response = client.get('/api/notifications',
            headers={'Authorization': f'Bearer {second_user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
        notification = response.json[0]
        assert 'from_profile' in notification
        assert 'name' in notification['from_profile']
    
    def test_notification_has_type(self, client, match_pair):
        """Notification should have type field."""
        response = client.get('/api/notifications',
            headers={'Authorization': f'Bearer {match_pair["user2"]["token"]}'}
        )
        
        if len(response.json) > 0:
            notification = response.json[0]
            assert notification['type'] in ['match', 'like', 'message']
    
    def test_notification_has_message(self, client, match_pair):
        """Notification should have message field."""
        response = client.get('/api/notifications',
            headers={'Authorization': f'Bearer {match_pair["user2"]["token"]}'}
        )
        
        if len(response.json) > 0:
            notification = response.json[0]
            assert 'message' in notification
            assert len(notification['message']) > 0