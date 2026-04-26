"""Initial schema

Revision ID: 96c9b7554393
Revises: 
Create Date: 2026-04-26 12:21:05.972792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96c9b7554393'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("verification_token", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_active", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("verification_token"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "profiles",
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("preferred_age_min", sa.Integer(), nullable=True),
        sa.Column("preferred_age_max", sa.Integer(), nullable=True),
        sa.Column("interests", sa.JSON(), nullable=True),
        sa.Column("profile_picture", sa.String(length=255), nullable=True),
        sa.Column("visibility", sa.Boolean(), nullable=True),
        sa.Column("gender", sa.String(length=50), nullable=True),
        sa.Column("gender_preference", sa.String(length=50), nullable=True),
        sa.Column("relationship_goal", sa.String(length=50), nullable=True),
        sa.Column("occupation", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("profile_id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_profiles_created_at", "profiles", ["created_at"], unique=False)
    op.create_index(
        "ix_profiles_gender_age", "profiles", ["gender", "age"], unique=False
    )
    op.create_index(
        "ix_profiles_relationship_goal",
        "profiles",
        ["relationship_goal"],
        unique=False,
    )
    op.create_index(
        "ix_profiles_visibility_created_at",
        "profiles",
        ["visibility", "created_at"],
        unique=False,
    )

    op.create_table(
        "likes",
        sa.Column("like_id", sa.Integer(), nullable=False),
        sa.Column("from_user_id", sa.Integer(), nullable=False),
        sa.Column("to_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["from_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["to_user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("like_id"),
        sa.UniqueConstraint("from_user_id", "to_user_id", name="unique_like"),
    )
    op.create_index("ix_likes_created_at", "likes", ["created_at"], unique=False)
    op.create_index(
        "ix_likes_to_user_status", "likes", ["to_user_id", "status"], unique=False
    )

    op.create_table(
        "matches",
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("user1_id", sa.Integer(), nullable=False),
        sa.Column("user2_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user1_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["user2_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("match_id"),
        sa.UniqueConstraint("user1_id", "user2_id", name="unique_match"),
    )
    op.create_index("ix_matches_created_at", "matches", ["created_at"], unique=False)
    op.create_index(
        "ix_matches_user1_created_at",
        "matches",
        ["user1_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_matches_user2_created_at",
        "matches",
        ["user2_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "notifications",
        sa.Column("notification_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.String(length=255), nullable=False),
        sa.Column("from_user_id", sa.Integer(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["from_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("notification_id"),
    )
    op.create_index(
        "ix_notifications_created_at", "notifications", ["created_at"], unique=False
    )
    op.create_index(
        "ix_notifications_from_user", "notifications", ["from_user_id"], unique=False
    )
    op.create_index(
        "ix_notifications_user_read_created",
        "notifications",
        ["user_id", "is_read", "created_at"],
        unique=False,
    )

    op.create_table(
        "messages",
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("receiver_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["receiver_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["sender_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index("ix_messages_created_at", "messages", ["created_at"], unique=False)
    op.create_index(
        "ix_messages_receiver_read", "messages", ["receiver_id", "read_at"], unique=False
    )
    op.create_index(
        "ix_messages_receiver_sender_created",
        "messages",
        ["receiver_id", "sender_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_messages_sender_receiver_created",
        "messages",
        ["sender_id", "receiver_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "bookmark",
        sa.Column("bookmark_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("bookmarked_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["bookmarked_user_id"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("bookmark_id"),
        sa.UniqueConstraint("user_id", "bookmarked_user_id", name="unique_bookmark"),
    )
    op.create_index("ix_bookmark_created_at", "bookmark", ["created_at"], unique=False)
    op.create_index(
        "ix_bookmark_user_created_at",
        "bookmark",
        ["user_id", "created_at"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_bookmark_user_created_at", table_name="bookmark")
    op.drop_index("ix_bookmark_created_at", table_name="bookmark")
    op.drop_table("bookmark")

    op.drop_index("ix_messages_sender_receiver_created", table_name="messages")
    op.drop_index("ix_messages_receiver_sender_created", table_name="messages")
    op.drop_index("ix_messages_receiver_read", table_name="messages")
    op.drop_index("ix_messages_created_at", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_notifications_user_read_created", table_name="notifications")
    op.drop_index("ix_notifications_from_user", table_name="notifications")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_matches_user2_created_at", table_name="matches")
    op.drop_index("ix_matches_user1_created_at", table_name="matches")
    op.drop_index("ix_matches_created_at", table_name="matches")
    op.drop_table("matches")

    op.drop_index("ix_likes_to_user_status", table_name="likes")
    op.drop_index("ix_likes_created_at", table_name="likes")
    op.drop_table("likes")

    op.drop_index("ix_profiles_visibility_created_at", table_name="profiles")
    op.drop_index("ix_profiles_relationship_goal", table_name="profiles")
    op.drop_index("ix_profiles_gender_age", table_name="profiles")
    op.drop_index("ix_profiles_created_at", table_name="profiles")
    op.drop_table("profiles")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
