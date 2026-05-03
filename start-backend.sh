#!/bin/bash

# Kill any process on port 5000
echo "Killing any process on port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 1

# Start Flask
echo "Starting Flask..."
source .venv/bin/activate
python run.py
