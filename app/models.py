"""
Database models for the dating application.

This module contains all SQLAlchemy models representing the application's
data entities, including users, profiles, matches, messages, and notifications.
"""

import secrets
import string
from datetime import datetime, timezone

from app import db


def utc_now():
    """
    Get current UTC timestamp.

    Returns:
        Current datetime in UTC timezone
    """
    return datetime.now(timezone.utc)


def generate_verification_token():
    """
    Generate a random verification token.

    Returns:
        Random 64-character alphanumeric string
    """
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(64)
    )


class User(db.Model):
    """
    User model representing application users.

    Attributes:
        user_id: Primary key
        email: User's email address (unique)
        password_hash: Hashed password
        is_verified: Email verification status
        verification_token: Token for email verification
        created_at: Account creation timestamp
        last_active: Last activity timestamp
        profile: One-to-one relationship with Profile
        likes_sent: Likes sent by this user
        likes_received: Likes received by this user
        notifications: User's notifications
    """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(
        db.String(64), unique=True, default=generate_verification_token
    )
    created_at = db.Column(db.DateTime, default=utc_now)
    last_active = db.Column(db.DateTime, default=utc_now)

    profile = db.relationship(
        "Profile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    likes_sent = db.relationship(
        "Like", foreign_keys="Like.from_user_id", backref="from_user", lazy="dynamic"
    )
    likes_received = db.relationship(
        "Like", foreign_keys="Like.to_user_id", backref="to_user", lazy="dynamic"
    )
    notifications = db.relationship(
        "Notification",
        foreign_keys="Notification.user_id",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.user_id,
            "email": self.email,
            "hashed_password": self.password_hash,
            "is_verified": self.is_verified,
            "verification_token": self.verification_token,
            "created_at": self.created_at,
            "last_active": self.last_active,
        }

    def __repr__(self):
        return f"<User {self.email}>"


class Profile(db.Model):
    """
    Profile model representing user profiles.

    Attributes:
        profile_id: Primary key
        user_id: Foreign key to User
        name: User's name
        age: User's age
        bio: User's biography
        preferred_age_min: Minimum age preference for matches
        preferred_age_max: Maximum age preference for matches
        interests: List of user interests
        profile_picture: URL/path to profile picture
        visibility: Whether profile is public
        gender: User's gender
        gender_preference: Gender preference for matches
        relationship_goal: User's relationship goal
        occupation: User's occupation
        created_at: Profile creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "profiles"
    __table_args__ = (
        db.Index("ix_profiles_visibility_created_at", "visibility", "created_at"),
        db.Index("ix_profiles_gender_age", "gender", "age"),
        db.Index("ix_profiles_relationship_goal", "relationship_goal"),
    )

    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=False, unique=True
    )

    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.Text)

    # Age preferences
    preferred_age_min = db.Column(db.Integer, default=18)
    preferred_age_max = db.Column(db.Integer, default=50)

    interests = db.Column(db.JSON, default=list)

    profile_picture = db.Column(db.String(255))

    visibility = db.Column(db.Boolean, default=True)

    gender = db.Column(db.String(50))
    gender_preference = db.Column(db.String(50), default="all")

    relationship_goal = db.Column(db.String(50))
    occupation = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "id": self.profile_id,
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "bio": self.bio,
            "preferred_age_min": self.preferred_age_min,
            "preferred_age_max": self.preferred_age_max,
            "interests": self.interests or [],
            "profile_picture": self.profile_picture,
            "visibility": self.visibility,
            "gender": self.gender,
            "gender_preference": self.gender_preference,
            "relationship_goal": self.relationship_goal,
            "occupation": self.occupation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Profile {self.name}>"


class Like(db.Model):
    """
    Like model representing user likes/dislikes.

    Attributes:
        like_id: Primary key
        from_user_id: User who sent the like
        to_user_id: User who received the like
        status: Type of interaction (liked, disliked, passed)
        created_at: Timestamp when like was created
    """

    __tablename__ = "likes"

    like_id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    status = db.Column(db.String(20), default="liked")  # 'liked', 'disliked', 'passed'
    created_at = db.Column(db.DateTime, default=utc_now, index=True)

    __table_args__ = (
        db.UniqueConstraint("from_user_id", "to_user_id", name="unique_like"),
        db.Index("ix_likes_to_user_status", "to_user_id", "status"),
    )

    def to_dict(self):
        return {
            "id": self.like_id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Match(db.Model):
    """
    Match model representing mutual matches between users.

    Attributes:
        match_id: Primary key
        user1_id: First user in the match
        user2_id: Second user in the match
        created_at: Timestamp when match was created
        user1: Relationship to first user
        user2: Relationship to second user
    """

    __tablename__ = "matches"

    match_id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, index=True)

    user1 = db.relationship("User", foreign_keys=[user1_id])
    user2 = db.relationship("User", foreign_keys=[user2_id])

    __table_args__ = (
        db.UniqueConstraint("user1_id", "user2_id", name="unique_match"),
        db.Index("ix_matches_user1_created_at", "user1_id", "created_at"),
        db.Index("ix_matches_user2_created_at", "user2_id", "created_at"),
    )

    def to_dict(self, include_profiles=False):
        result = {
            "id": self.match_id,
            "user1_id": self.user1_id,
            "user2_id": self.user2_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        return result


class Notification(db.Model):
    """
    Notification model representing user notifications.

    Attributes:
        notification_id: Primary key
        user_id: User who receives the notification
        type: Type of notification (match, like, message)
        message: Notification message content
        from_user_id: User who triggered the notification
        is_read: Whether notification has been read
        created_at: Timestamp when notification was created
    """

    __tablename__ = "notifications"
    __table_args__ = (
        db.Index(
            "ix_notifications_user_read_created",
            "user_id",
            "is_read",
            "created_at",
        ),
        db.Index("ix_notifications_from_user", "from_user_id"),
    )

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'match', 'like', 'message'
    message = db.Column(db.String(255), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now, index=True)

    gets = db.relationship("User", foreign_keys=[from_user_id])

    def to_dict(self):
        return {
            "id": self.notification_id,
            "user_id": self.user_id,
            "type": self.type,
            "message": self.message,
            "from_user_id": self.from_user_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Message(db.Model):
    """
    Message model representing private messages between users.

    Attributes:
        message_id: Primary key
        sender_id: User who sent the message
        receiver_id: User who received the message
        content: Message content
        created_at: Timestamp when message was created
        read_at: Timestamp when message was read
        sender: Relationship to sender user
        receiver: Relationship to receiver user
    """

    __tablename__ = "messages"
    __table_args__ = (
        db.Index("ix_messages_receiver_read", "receiver_id", "read_at"),
        db.Index(
            "ix_messages_sender_receiver_created",
            "sender_id",
            "receiver_id",
            "created_at",
        ),
        db.Index(
            "ix_messages_receiver_sender_created",
            "receiver_id",
            "sender_id",
            "created_at",
        ),
    )

    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    read_at = db.Column(db.DateTime, nullable=True)

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

    def to_dict(self):
        return {
            "id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "is_read": self.read_at is not None,
        }

    def to_dict_extended(self, current_user_id):
        data = self.to_dict()
        data["is_sent"] = self.sender_id == current_user_id
        return data


class Bookmark(db.Model):
    """
    Bookmark model representing user bookmarks/favorites.

    Attributes:
        bookmark_id: Primary key
    """

    __tablename__ = "bookmark"

    bookmark_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    bookmarked_user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=utc_now, index=True)

    user = db.relationship("User", foreign_keys=[user_id])
    bookmarks = db.relationship("User", foreign_keys=[bookmarked_user_id])

    __table_args__ = (
        db.UniqueConstraint("user_id", "bookmarked_user_id", name="unique_bookmark"),
        db.Index("ix_bookmark_user_created_at", "user_id", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.bookmark_id,
            "user_id": self.user_id,
            "bookmarked_user_id": self.bookmarked_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
