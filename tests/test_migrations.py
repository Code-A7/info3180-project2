"""Test cases for database migrations."""

import os
import shutil
import tempfile

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app import create_app, db
from app.config import TestingConfig


class TestMigrations:
    """Test database migrations using Alembic."""

    @pytest.fixture
    def migration_app(self):
        """Create a test app with a temporary database for migration testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "migration_test.db")

        class MigrationTestingConfig(TestingConfig):
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
            SQLALCHEMY_ENGINE_OPTIONS = {}

        app = create_app(MigrationTestingConfig)

        with app.app_context():
            yield app, db_path

        shutil.rmtree(temp_dir, ignore_errors=True)

    def get_alembic_config(self, db_path):
        """Get Alembic configuration for testing."""
        alembic_cfg = Config("migrations/alembic.ini")
        alembic_cfg.set_main_option("script_location", "migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
        return alembic_cfg

    def test_migration_upgrade_from_scratch(self, migration_app):
        """Test that migrations can be applied from scratch to create all tables."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Run all migrations
        command.upgrade(alembic_cfg, "head")

        # Verify all tables were created
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            expected_tables = {
                "users",
                "profiles",
                "likes",
                "matches",
                "notifications",
                "messages",
                "bookmark",
                "alembic_version",
            }

            assert expected_tables.issubset(
                set(tables)
            ), f"Missing tables: {expected_tables - set(tables)}"

    def test_migration_downgrade(self, migration_app):
        """Test that migrations can be downgraded."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # First upgrade to head
        command.upgrade(alembic_cfg, "head")

        # Verify tables exist
        with app.app_context():
            inspector = inspect(db.engine)
            tables_before = inspector.get_table_names()
            assert "users" in tables_before

        # Now downgrade to base (empty database)
        command.downgrade(alembic_cfg, "base")

        # Verify tables are gone (except alembic_version might remain)
        with app.app_context():
            inspector = inspect(db.engine)
            tables_after = inspector.get_table_names()
            # After downgrade, only alembic_version should remain
            assert "users" not in tables_after
            assert "profiles" not in tables_after

    def test_migration_upgrade_downgrade_cycle(self, migration_app):
        """Test that upgrade and downgrade can be performed multiple times."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # First cycle: upgrade -> downgrade
        command.upgrade(alembic_cfg, "head")
        command.downgrade(alembic_cfg, "base")

        # Second cycle: upgrade -> downgrade
        command.upgrade(alembic_cfg, "head")
        command.downgrade(alembic_cfg, "base")

        # Verify final state is clean
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            assert "users" not in tables
            assert "profiles" not in tables

    def test_migration_creates_correct_columns(self, migration_app):
        """Test that migration creates all expected columns in users table."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Run migrations
        command.upgrade(alembic_cfg, "head")

        # Check users table columns
        with app.app_context():
            inspector = inspect(db.engine)
            columns = inspector.get_columns("users")
            column_names = {col["name"] for col in columns}

            expected_columns = {
                "user_id",
                "email",
                "password_hash",
                "is_verified",
                "verification_token",
                "created_at",
                "last_active",
            }

            assert expected_columns.issubset(
                column_names
            ), f"Missing columns in users table: {expected_columns - column_names}"

    def test_migration_creates_correct_indexes(self, migration_app):
        """Test that migration creates expected indexes."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Run migrations
        command.upgrade(alembic_cfg, "head")

        # Check indexes on users table
        with app.app_context():
            inspector = inspect(db.engine)
            indexes = inspector.get_indexes("users")
            index_names = {idx["name"] for idx in indexes}

            # Should have at least the email index
            assert any(
                "email" in idx_name for idx_name in index_names
            ), "Email index not found"

    def test_migration_creates_foreign_keys(self, migration_app):
        """Test that migration creates proper foreign key constraints."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Run migrations
        command.upgrade(alembic_cfg, "head")

        # Check foreign keys in profiles table
        with app.app_context():
            inspector = inspect(db.engine)
            foreign_keys = inspector.get_foreign_keys("profiles")

            # Should have foreign key to users table
            assert len(foreign_keys) > 0, "No foreign keys found in profiles table"
            assert any(
                fk["referred_table"] == "users" for fk in foreign_keys
            ), "Foreign key to users table not found"

    def test_migration_handles_empty_database(self, migration_app):
        """Test that migration works correctly on a completely empty database."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Verify database is empty
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            assert len(tables) == 0, "Database should be empty initially"

        # Run migrations - should work without errors
        try:
            command.upgrade(alembic_cfg, "head")
        except Exception as e:
            pytest.fail(f"Migration failed on empty database: {str(e)}")

        # Verify tables were created
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            assert len(tables) > 0, "No tables created after migration"

    def test_migration_idempotency(self, migration_app):
        """Test that running migrations multiple times is idempotent."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Run migrations first time
        command.upgrade(alembic_cfg, "head")

        # Get current state
        with app.app_context():
            inspector = inspect(db.engine)
            tables_after_first = set(inspector.get_table_names())

        # Run migrations second time - should not change anything
        command.upgrade(alembic_cfg, "head")

        # Verify state is the same
        with app.app_context():
            inspector = inspect(db.engine)
            tables_after_second = set(inspector.get_table_names())

        assert (
            tables_after_first == tables_after_second
        ), "Running migrations twice changed the database state"

    def test_migration_creates_all_required_tables(self, migration_app):
        """Test that all required tables are created by migrations."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Run migrations
        command.upgrade(alembic_cfg, "head")

        required_tables = [
            "users",
            "profiles",
            "likes",
            "matches",
            "notifications",
            "messages",
            "bookmark",
        ]

        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            for table in required_tables:
                assert (
                    table in tables
                ), f"Required table '{table}' not created by migration"

    def test_migration_preserves_data_during_upgrade(self, migration_app):
        """Test that data is preserved during migration upgrade."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Run migrations
        command.upgrade(alembic_cfg, "head")

        # Insert test data
        with app.app_context():
            from app.models import User

            user = User(
                email="test_migration@example.com",
                password_hash="hashed_password",
                is_verified=True,
            )
            db.session.add(user)
            db.session.commit()

            # Verify data was inserted
            count_before = db.session.query(User).count()
            assert count_before == 1

        # Run migrations again (should be idempotent)
        command.upgrade(alembic_cfg, "head")

        # Verify data is still there
        with app.app_context():
            count_after = db.session.query(User).count()
            assert count_after == 1, "Data was lost during migration"

    def test_migration_rollback_scenario(self, migration_app):
        """Test a complete migration scenario: upgrade, insert data, downgrade, upgrade again."""
        app, db_path = migration_app
        alembic_cfg = self.get_alembic_config(db_path)

        # Upgrade to head
        command.upgrade(alembic_cfg, "head")

        # Insert test data
        with app.app_context():
            from app.models import User

            user = User(
                email="rollback_test@example.com",
                password_hash="hashed_password",
                is_verified=True,
            )
            db.session.add(user)
            db.session.commit()

        # Downgrade to base
        command.downgrade(alembic_cfg, "base")

        # Upgrade again
        command.upgrade(alembic_cfg, "head")

        # Verify tables are back
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            assert "users" in tables
            assert "profiles" in tables
