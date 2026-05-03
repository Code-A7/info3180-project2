"""
Application factory and initialization.

This module contains the application factory function that creates and configures
the Flask application instance, including database setup, blueprint registration,
and WebSocket configuration.
"""

import os

from flask import Flask, current_app, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO()
migrate = Migrate()


# Store user sessions for WebSocket
connected_users = {}


def create_app(config_class=Config):
    """
    Create and configure the Flask application instance.

    Args:
        config_class: Configuration class to use (defaults to Config)

    Returns:
        Configured Flask application instance

    This function:
    - Creates the Flask app with the specified configuration
    - Initializes database, authentication, and WebSocket extensions
    - Sets up CORS for API endpoints
    - Registers blueprints for different application modules
    - Configures WebSocket event handlers
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["WTF_CSRF_ENABLED"] = False

    # Configure CORS for production
    cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")

    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    socketio.init_app(app, cors_allowed_origins=cors_origins, async_mode="threading")

    # Serve uploaded files
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        """
        Serve uploaded files from the uploads directory.

        Args:
            filename: Name of the file to serve

        Returns:
            File response from the uploads directory
        """
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "./uploads")
        if not os.path.isabs(upload_folder):
            upload_folder = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), upload_folder
            )
        return send_from_directory(upload_folder, filename)

    # Register blueprints
    from app import matches, messages, notifications, views

    app.register_blueprint(views.bp)
    app.register_blueprint(matches.bp)
    app.register_blueprint(notifications.bp_notifications)
    app.register_blueprint(messages.bp_messages)

    # Set socket emit function
    from app.matches import set_socket_emit

    set_socket_emit(
        lambda user_id, event, data: socketio.emit(event, data, room=f"user_{user_id}")
    )

    # WebSocket events
    @socketio.on("connect")
    def handle_connect(auth=None):
        """
        Handle WebSocket connection event.

        Args:
            auth: Optional authentication data
        """
        print(f"Client connected: {auth}")

    @socketio.on("disconnect")
    def handle_disconnect():
        """Handle WebSocket disconnection event."""
        print("Client disconnected")

    @socketio.on("subscribe")
    def handle_subscribe(data):
        """
        Handle user subscription to WebSocket channel.

        Args:
            data: Subscription data containing user_id
        """
        user_id = data.get("user_id")
        if user_id:
            connected_users[user_id] = True
            print(f"User {user_id} subscribed")

    @socketio.on("unsubscribe")
    def handle_unsubscribe(data):
        """
        Handle user unsubscription from WebSocket channel.

        Args:
            data: Unsubscription data containing user_id
        """
        user_id = data.get("user_id")
        if user_id and user_id in connected_users:
            del connected_users[user_id]

    return app


# SEED DATABASE
# subprocess.run(["python", "seed.py"])
