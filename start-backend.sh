#!/bin/bash

# Startup script for Render deployment
# This script runs database migrations and starts the Flask app

echo "Starting DriftDater backend..."

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Start the Flask application with Gunicorn
echo "Starting Flask app with Gunicorn..."
exec gunicorn -k eventlet -w 1 --bind 0.0.0.0:$PORT run:app
