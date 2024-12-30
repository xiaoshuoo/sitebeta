#!/usr/bin/env bash
# exit on error
set -o errexit

# Add the project directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/opt/render/project/src

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
