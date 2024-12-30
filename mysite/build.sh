#!/usr/bin/env bash
# exit on error
set -o errexit

# Create directories
mkdir -p /opt/render/project/src/staticfiles
mkdir -p /opt/render/project/src/media/avatars
mkdir -p /opt/render/project/src/media/posts
mkdir -p /opt/render/project/src/media/covers
mkdir -p /opt/render/project/src/media/thumbnails

# Set permissions
chmod -R 777 /opt/render/project/src/media
chmod -R 777 /opt/render/project/src/staticfiles

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create static directory if it doesn't exist
python -c "import os; os.makedirs('static', exist_ok=True)"

# Clean up old static files
rm -rf /opt/render/project/src/staticfiles/*

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Print success message
echo "Build completed successfully"

# Start gunicorn in the background and save PID
gunicorn config.wsgi:application \
    --bind=0.0.0.0:$PORT \
    --workers=4 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --daemon \
    --pid gunicorn.pid

# Wait a few seconds for gunicorn to start
sleep 5

# Check if gunicorn is running
if ps aux | grep -q "[g]unicorn"; then
    echo "Gunicorn started successfully"
    # Keep the script running to prevent container from stopping
    tail -f /dev/null
else
    echo "Failed to start Gunicorn"
    exit 1
fi
