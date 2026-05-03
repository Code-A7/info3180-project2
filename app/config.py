import os
import secrets

from dotenv import load_dotenv

load_dotenv()


def get_env_var(name, default=None, required=False):
    """Get environment variable with optional validation."""
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        value = default
    if required and not value:
        raise ValueError(f"Required environment variable {name} is not set")
    return value


def get_bool_env_var(name, default=False):
    """Read a boolean environment variable."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Base configuration with security defaults."""

    # Security
    SECRET_KEY = get_env_var("SECRET_KEY") or secrets.token_hex(32)

    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Database
    SQLALCHEMY_DATABASE_URI = get_env_var(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///driftdater.db"
    ).replace("postgres://", "postgresql://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # File uploads
    UPLOAD_FOLDER = get_env_var("UPLOAD_FOLDER", "./uploads")
    MAX_CONTENT_LENGTH = int(get_env_var("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_FILENAME_LENGTH = 255

    # Mail. Use EMAIL_PROVIDER=resend in production on hosts that block SMTP.
    RESEND_API_KEY = get_env_var("RESEND_API_KEY")
    EMAIL_PROVIDER = get_env_var(
        "EMAIL_PROVIDER", "resend" if RESEND_API_KEY else "smtp"
    ).lower()
    EMAIL_FROM = get_env_var("EMAIL_FROM")
    RESEND_API_URL = get_env_var("RESEND_API_URL", "https://api.resend.com/emails")

    # SMTP_* is preferred; MAILTRAP_* is kept for existing local configs.
    SMTP_HOST = get_env_var(
        "SMTP_HOST", get_env_var("MAILTRAP_SMTP_HOST", "sandbox.smtp.mailtrap.io")
    )
    SMTP_PORT = int(get_env_var("SMTP_PORT", get_env_var("MAILTRAP_SMTP_PORT", 2525)))
    SMTP_USER = get_env_var("SMTP_USER", get_env_var("MAILTRAP_SMTP_USER"))
    SMTP_PASS = get_env_var("SMTP_PASS", get_env_var("MAILTRAP_SMTP_PASS"))
    SMTP_FROM_EMAIL = get_env_var(
        "SMTP_FROM_EMAIL",
        get_env_var("MAILTRAP_FROM_EMAIL", "DriftDater <noreply@driftdater.com>"),
    )
    EMAIL_FROM = EMAIL_FROM or SMTP_FROM_EMAIL
    SMTP_USE_TLS = get_bool_env_var("SMTP_USE_TLS", True)
    SMTP_USE_SSL = get_bool_env_var("SMTP_USE_SSL", False)

    MAILTRAP_SMTP_HOST = SMTP_HOST
    MAILTRAP_SMTP_PORT = SMTP_PORT
    MAILTRAP_SMTP_USER = SMTP_USER
    MAILTRAP_SMTP_PASS = SMTP_PASS
    MAILTRAP_FROM_EMAIL = SMTP_FROM_EMAIL

    # Frontend URL for email links
    FRONTEND_URL = get_env_var("FRONTEND_URL", "http://localhost:5173")

    # JWT Configuration
    JWT_SECRET_KEY = get_env_var("JWT_SECRET_KEY") or secrets.token_hex(32)
    JWT_ACCESS_TOKEN_EXPIRES = 604800

    # CORS
    CORS_ORIGINS = get_env_var("CORS_ORIGINS", "*").split(",")

    @classmethod
    def init_app(cls, app):
        """Initialize application."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = get_env_var(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED = False
    SMTP_USER = None
    SMTP_PASS = None
    MAILTRAP_SMTP_USER = None
    MAILTRAP_SMTP_PASS = None


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(env=None):
    """Get configuration based on environment."""
    if env is None:
        env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])
