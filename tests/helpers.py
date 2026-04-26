import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, bcrypt
from app.models import User, Profile


def create_user(app, email, is_verified=True, password="TestPass123!"):
    """Create a test user with the given email and verification status."""
    with app.app_context():
        user = User(
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            is_verified=is_verified,
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user.user_id


def create_profile(app, user_id, **kwargs):
    """Create a test profile with customizable fields."""
    with app.app_context():
        defaults = {
            "user_id": user_id,
            "name": kwargs.get("name", f"User {user_id}"),
            "age": kwargs.get("age", 25),
            "bio": kwargs.get("bio", "Test bio"),
            "preferred_age_min": kwargs.get("preferred_age_min", 18),
            "preferred_age_max": kwargs.get("preferred_age_max", 50),
            "interests": kwargs.get("interests", ["hiking", "reading", "music"]),
            "gender": kwargs.get("gender", "male"),
            "gender_preference": kwargs.get("gender_preference", "all"),
            "relationship_goal": kwargs.get(
                "relationship_goal", "serious_relationship"
            ),
            "occupation": kwargs.get("occupation", "Developer"),
            "visibility": kwargs.get("visibility", True),
        }

        profile = Profile(**defaults)
        db.session.add(profile)
        db.session.commit()
        db.session.refresh(profile)
        return profile


def get_auth_token(client, email, password="TestPass123!"):
    """Get authentication token for a user."""
    response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    if response.status_code != 200:
        raise ValueError(f"Login failed for {email}: {response.json}")
    return response.json["token"]


def create_test_user(
    client,
    app,
    email,
    password="TestPass123!",
    name="Test User",
    age=25,
    gender="male",
    interests=None,
    gender_preference="all",
    relationship_goal="dating",
    is_verified=True,
):
    """Create a complete test user with profile and return user_id."""
    if interests is None:
        interests = ["music", "travel"]

    client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "confirm_password": password},
    )

    with app.app_context():
        user = db.session.query(User).filter_by(email=email).first()
        user.is_verified = is_verified
        db.session.commit()
        user_id = user.user_id

        profile = Profile(
            user_id=user_id,
            name=name,
            age=age,
            bio="Test bio",
            gender=gender,
            gender_preference=gender_preference,
            interests=interests,
            relationship_goal=relationship_goal,
        )
        db.session.add(profile)
        db.session.commit()

    return user_id


def create_incompatible_profile(app, user_id):
    """Create an incompatible profile for testing filters."""
    return create_profile(
        app,
        user_id,
        name="Incompatible",
        age=55,
        interests=["gaming"],
        gender="male",
        gender_preference="all",
        relationship_goal="friendship",
    )


def get_unverified_user(client, app, email="unverified@example.com"):
    """Create an unverified user and return their credentials."""
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
        },
    )

    with app.app_context():
        user = db.session.query(User).filter_by(email=email).first()
        user_id = user.user_id

    return {"user_id": user_id, "email": email}


def create_mutual_match(client, app, user1_id, user2_id, token1):
    """Create a mutual match between two users. Returns the match object."""
    from app.models import Match

    # User1 likes User2
    client.post(
        f"/api/matches/like/{user2_id}", headers={"Authorization": f"Bearer {token1}"}
    )

    # Get token for user2
    with app.app_context():
        user2 = (
            db.session.query(User)
            .filter_by(email=User.query.get(user2_id).email)
            .first()
        )

    response = client.post(
        "/api/auth/login", json={"email": user2.email, "password": "TestPass123!"}
    )
    token2 = response.json["token"]

    # User2 likes User1 (mutual match)
    client.post(
        f"/api/matches/like/{user1_id}", headers={"Authorization": f"Bearer {token2}"}
    )

    with app.app_context():
        match = Match.query.filter(
            ((Match.user1_id == user1_id) & (Match.user2_id == user2_id))
            | ((Match.user1_id == user2_id) & (Match.user2_id == user1_id))
        ).first()
        return match


def verify_user(app, email):
    """Verify a user's email."""
    with app.app_context():
        user = db.session.query(User).filter_by(email=email).first()
        user.is_verified = True
        db.session.commit()
