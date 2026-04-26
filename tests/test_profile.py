import pytest
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db


class TestCreateProfile:
    """Test profile creation functionality."""
    
    def test_create_profile_unauthorized(self, client):
        """Should return 401 when not authenticated."""
        response = client.post('/api/profile', json={
            'name': 'John',
            'age': 25,
            'interests': 'hiking, reading, music'
        })
        
        assert response.status_code == 401
    
    def test_create_profile_success(self, client, verified_user):
        """Should create profile with valid data."""
        response = client.post('/api/profile', 
            json={
                'name': 'John Doe',
                'age': 25,
                'bio': 'I love hiking and outdoor activities',
                'interests': 'hiking, reading, music, cooking, travel',
                'gender': 'male',
                'gender_preference': 'all',
                'relationship_goal': 'serious_relationship',
                'occupation': 'Developer',
                'visibility': True
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 201
        assert response.json['name'] == 'John Doe'
        assert response.json['age'] == 25
        assert response.json['gender'] == 'male'
    
    def test_create_profile_insufficient_interests(self, client, verified_user):
        """Should fail with less than 3 interests."""
        response = client.post('/api/profile', 
            json={
                'name': 'John',
                'age': 25,
                'gender': 'male',
                'gender_preference': 'female',
                'relationship_goal': 'friendship',
                'interests': 'hiking, reading'
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400
        assert 'interests' in response.json.get('errors', {}) or 'interests' in response.json.get('errors', {})
    
    def test_create_profile_age_too_young(self, client, verified_user):
        """Should fail if age is below 18."""
        response = client.post('/api/profile', 
            json={
                'name': 'Young User',
                'age': 16,
                'interests': 'hiking, reading, music, gaming, travel'
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400
    
    def test_create_profile_duplicate(self, client, user_with_profile):
        """Should fail if profile already exists."""
        response = client.post('/api/profile', 
            json={
                'name': 'Another Name',
                'age': 30,
                'interests': 'cooking, gaming, reading, art, music'
            },
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 400
        assert 'already exists' in response.json['error'].lower()
    
    def test_create_profile_missing_name(self, client, verified_user):
        """Should fail if name is missing."""
        response = client.post('/api/profile', 
            json={
                'age': 25,
                'interests': 'hiking, reading, music, gaming, travel'
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400
    
    def test_create_profile_missing_age(self, client, verified_user):
        """Should fail if age is missing."""
        response = client.post('/api/profile', 
            json={
                'name': 'John',
                'interests': 'hiking, reading, music, gaming, travel'
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400


class TestGetProfile:
    """Test getting profile functionality."""
    
    def test_get_profile_success(self, client, user_with_profile):
        """Should return user's own profile."""
        response = client.get('/api/profile',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
        assert response.json['name'] == 'Test User'
        assert response.json['age'] == 25
        assert 'interests' in response.json
    
    def test_get_profile_unauthorized(self, client):
        """Should return 401 when not authenticated."""
        response = client.get('/api/profile')
        
        assert response.status_code == 401
    
    def test_get_profile_not_found(self, client, verified_user):
        """Should return 404 when profile doesn't exist."""
        response = client.get('/api/profile',
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 404


class TestUpdateProfile:
    """Test profile update functionality."""
    
    def test_update_profile_success(self, client, user_with_profile):
        """Should update profile with valid data."""
        response = client.put('/api/profile',
            json={
                'name': 'Jane Doe',
                'age': 26,
                'bio': 'Updated bio',
                'interests': 'hiking, reading, music, cooking, gaming',
                'gender': 'female',
                'gender_preference': 'male',
                'relationship_goal': 'marriage',
                'occupation': 'Designer',
                'visibility': True
            },
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
        assert response.json['name'] == 'Jane Doe'
        assert response.json['age'] == 26
        assert response.json['gender'] == 'female'
    
    def test_update_profile_not_found(self, client, verified_user):
        """Should return 404 when no profile exists."""
        response = client.put('/api/profile',
            json={'name': 'John'},
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 404
    
    def test_update_profile_unauthorized(self, client):
        """Should return 401 when not authenticated."""
        response = client.put('/api/profile',
            json={'name': 'John'},
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 401
    
    def test_update_profile_insufficient_interests(self, client, user_with_profile):
        """Should fail with less than 3 interests."""
        response = client.put('/api/profile',
            json={'name': 'John', 'interests': 'hiking'},
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 400


class TestViewOtherProfile:
    """Test viewing other user's profiles."""
    
    def test_view_other_profile_public(self, client, app, second_user_with_profile):
        """Should view public profile of another user."""
        with app.app_context():
            profile = second_user_with_profile
            profile_id = profile['user_id']
        
        response = client.get(f'/api/profile/{profile_id}')
        
        assert response.status_code == 200
        assert response.json['name'] == 'Second User'
    
    def test_view_other_profile_private(self, client, app):
        """Should return 403 when viewing private profile without auth."""
        with app.app_context():
            from app.models import Profile, User
            
            # Create a user with private profile
            from tests.helpers import create_user
            
            user_id = create_user(app, 'private@example.com')
            
            profile = Profile(
                user_id=user_id,
                name='Private User',
                age=25,
                interests=['reading', 'writing', 'coding', 'gaming', 'music'],
                visibility=False
            )
            db.session.add(profile)
            db.session.commit()
            profile_id = user_id
        
        response = client.get(f'/api/profile/{profile_id}')
        
        assert response.status_code == 403
    
    def test_view_other_profile_private_authenticated_owner(self, client, app, verified_user):
        """Owner should be able to view their own private profile."""
        with app.app_context():
            from app.models import Profile
            profile = Profile(
                user_id=verified_user['user_id'],
                name='Private Owner',
                age=25,
                interests=['reading', 'writing', 'coding', 'gaming', 'music'],
                visibility=False
            )
            db.session.add(profile)
            db.session.commit()
        
        response = client.get('/api/profile',
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 200
        
        # Owner views own profile by user_id
        response = client.get(f'/api/profile/{verified_user["user_id"]}',
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 200
    
    def test_view_other_profile_not_found(self, client):
        """Should return 404 for non-existent profile."""
        response = client.get('/api/profile/99999')
        
        assert response.status_code == 404


class TestProfilePictureUpload:
    """Test profile picture upload functionality."""
    
    def test_upload_picture_success_jpg(self, client, user_with_profile):
        """Should upload JPG picture successfully."""
        data = {
            'file': (io.BytesIO(b'fake image content'), 'test.jpg')
        }
        
        response = client.post(
            '/api/profile/picture',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
        assert 'filename' in response.json
    
    def test_upload_picture_success_png(self, client, user_with_profile):
        """Should upload PNG picture successfully."""
        data = {
            'file': (io.BytesIO(b'fake image content'), 'test.png')
        }
        
        response = client.post(
            '/api/profile/picture',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
    
    def test_upload_picture_success_webp(self, client, user_with_profile):
        """Should upload WebP picture successfully."""
        data = {
            'file': (io.BytesIO(b'fake webp content'), 'test.webp')
        }
        
        response = client.post(
            '/api/profile/picture',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 200
    
    def test_upload_picture_no_file(self, client, user_with_profile):
        """Should fail when no file is provided."""
        response = client.post(
            '/api/profile/picture',
            data={},
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 400
        assert 'No file' in response.json['error']
    
    def test_upload_picture_invalid_extension(self, client, user_with_profile):
        """Should reject files with invalid extensions."""
        data = {
            'file': (io.BytesIO(b'fake executable'), 'test.exe')
        }
        
        response = client.post(
            '/api/profile/picture',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 400
    
    def test_upload_picture_empty_filename(self, client, user_with_profile):
        """Should reject files with empty filename."""
        data = {
            'file': (io.BytesIO(b'fake content'), '')
        }
        
        response = client.post(
            '/api/profile/picture',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {user_with_profile["token"]}'}
        )
        
        assert response.status_code == 400
    
    def test_upload_picture_unauthorized(self, client):
        """Should return 401 when not authenticated."""
        data = {
            'file': (io.BytesIO(b'fake image content'), 'test.jpg')
        }
        
        response = client.post(
            '/api/profile/picture',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 401
    
    def test_upload_picture_no_profile(self, client, verified_user):
        """Should fail when user has no profile."""
        data = {
            'file': (io.BytesIO(b'fake image content'), 'test.jpg')
        }
        
        response = client.post(
            '/api/profile/picture',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400
        assert 'Create a profile' in response.json['error']


class TestProfileValidation:
    """Test profile validation rules."""
    
    def test_profile_name_min_length(self, client, verified_user):
        """Name should be at least 2 characters."""
        response = client.post('/api/profile', 
            json={
                'name': 'A',
                'age': 25,
                'interests': 'hiking, reading, music, gaming, travel'
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400
    
    def test_profile_name_max_length(self, client, verified_user):
        """Name should be at most 100 characters."""
        response = client.post('/api/profile', 
            json={
                'name': 'A' * 101,
                'age': 25,
                'interests': 'hiking, reading, music, gaming, travel'
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400
    
    def test_profile_bio_max_length(self, client, verified_user):
        """Bio should be at most 500 characters."""
        response = client.post('/api/profile', 
            json={
                'name': 'Test User',
                'age': 25,
                'bio': 'A' * 501,
                'interests': 'hiking, reading, music, gaming, travel'
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400
    
    def test_profile_occupation_max_length(self, client, verified_user):
        """Occupation should be at most 100 characters."""
        response = client.post('/api/profile', 
            json={
                'name': 'Test User',
                'age': 25,
                'interests': 'hiking, reading, music, gaming, travel',
                'occupation': 'A' * 101
            },
            headers={'Authorization': f'Bearer {verified_user["token"]}'}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.parametrize("gender", [
        "male", "female", "non_binary", "other", "prefer_not_to_say"
    ])
    def test_profile_valid_genders(self, client, app, gender):
        """All valid gender options should be accepted."""
        # Create a new user for each gender test to avoid conflicts
        client.post('/api/auth/register', json={
            'email': f'gender_test_{gender}@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        })
        
        with app.app_context():
            from app.models import User
            user = db.session.query(User).filter_by(email=f'gender_test_{gender}@example.com').first()
            user.is_verified = True
            db.session.commit()
            user_id = user.user_id
        
        response = client.post('/api/auth/login', json={
            'email': f'gender_test_{gender}@example.com',
            'password': 'TestPass123!'
        })
        token = response.json['token']
        
        response = client.post('/api/profile', 
            json={
                'name': 'Test User',
                'age': 25,
                'gender': gender,
                'gender_preference': 'all',
                'relationship_goal': 'casual_dating',
                'interests': 'hiking, reading, music, gaming, travel'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 201
    
    @pytest.mark.parametrize("goal", [
        "friendship", "casual_dating", "serious_relationship", "marriage"
    ])
    def test_profile_valid_relationship_goals(self, client, app, goal):
        """All valid relationship goals should be accepted."""
        # Create a new user for each goal test to avoid conflicts
        client.post('/api/auth/register', json={
            'email': f'goal_test_{goal}@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        })
        
        with app.app_context():
            from app.models import User
            user = db.session.query(User).filter_by(email=f'goal_test_{goal}@example.com').first()
            user.is_verified = True
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': f'goal_test_{goal}@example.com',
            'password': 'TestPass123!'
        })
        token = response.json['token']
        
        response = client.post('/api/profile', 
            json={
                'name': 'Test User',
                'age': 25,
                'gender': 'male',
                'gender_preference': 'all',
                'relationship_goal': goal,
                'interests': 'hiking, reading, music, gaming, travel'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 201