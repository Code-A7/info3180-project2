import secrets
import string
from datetime import datetime, timezone

from app import db


def utc_now():
    return datetime.now(timezone.utc)


def generate_verification_token():
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(64)
    )


class User(db.Model):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
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
            "id": self.uid,
            "email": self.email,
            "hashed password": self.password_hash,
            "is_verified": self.is_verified,
            "verification_token": self.verification_token,
            "created_at": self.created_at,
            "last_active": self.last_active,
        }

    def __repr__(self):
        return f"<User {self.email}>"


class Profile(db.Model):
    __tablename__ = "profiles"

    pid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.uid"), nullable=False, unique=True
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

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "id": self.pid,
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
    __tablename__ = "likes"

    lid = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    status = db.Column(db.String(20), default="liked")  # 'liked', 'disliked', 'passed'
    created_at = db.Column(db.DateTime, default=utc_now)

    __table_args__ = (
        db.UniqueConstraint("from_user_id", "to_user_id", name="unique_like"),
    )

    def to_dict(self):
        return {
            "id": self.lid,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Match(db.Model):
    __tablename__ = "matches"

    mid = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    user1 = db.relationship("User", foreign_keys=[user1_id])
    user2 = db.relationship("User", foreign_keys=[user2_id])

    __table_args__ = (db.UniqueConstraint("user1_id", "user2_id", name="unique_match"),)

    def to_dict(self, include_profiles=False):
        result = {
            "id": self.mid,
            "user1_id": self.user1_id,
            "user2_id": self.user2_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        return result


class Notification(db.Model):
    __tablename__ = "notifications"

    nid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'match', 'like', 'message'
    message = db.Column(db.String(255), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    gets = db.relationship("User", foreign_keys=[from_user_id])

    def to_dict(self):
        return {
            "id": self.nid,
            "user_id": self.user_id,
            "type": self.type,
            "message": self.message,
            "from_user_id": self.from_user_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Message(db.Model):
    __tablename__ = "messages"

    meid = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    read_at = db.Column(db.DateTime, nullable=True)

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

    def to_dict(self):
        return {
            "id": self.meid,
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
    __tablename__ = "bookmark"

    bid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    bookmarked_user_id = db.Column(
        db.Integer, db.ForeignKey("users.uid"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=utc_now)

    user = db.relationship("User", foreign_keys=[user_id])
    bookmarks = db.relationship("User", foreign_keys=[bookmarked_user_id])

    __table_args__ = (
        db.UniqueConstraint("user_id", "bookmarked_user_id", name="unique_bookmark"),
    )

    def to_dict(self):
        return {
            "id": self.bid,
            "user_id": self.user_id,
            "bookmarked_user_id": self.bookmarked_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
