"""Add location column to profiles table

Revision ID: a1b2c3d4e5f6
Revises: 96c9b7554393
Create Date: 2026-05-04

Adds the location field to profiles (required for location-based matching).
preferred_age_min/max already exist in the initial schema.
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "96c9b7554393"
branch_labels = None
depends_on = None


def upgrade():
    """Add location column and index to profiles table."""
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.add_column(
            sa.Column("location", sa.String(length=150), nullable=True)
        )
        batch_op.create_index("ix_profiles_location", ["location"])


def downgrade():
    """Remove location column and index from profiles table."""
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.drop_index("ix_profiles_location")
        batch_op.drop_column("location")
