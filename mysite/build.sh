#!/usr/bin/env bash
# exit on error
set -o errexit

# Create media directories first
mkdir -p /opt/render/project/src/media/avatars
mkdir -p /opt/render/project/src/media/posts
mkdir -p /opt/render/project/src/media/covers
mkdir -p /opt/render/project/src/media/thumbnails

# Set permissions
chmod -R 777 /opt/render/project/src/media

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Start gunicorn
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT --workers=4
