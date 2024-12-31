#!/usr/bin/env bash
# exit on error
set -o errexit

# Create directories for static and media files
mkdir -p staticfiles
mkdir -p media

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input --clear

# Apply database migrations
python manage.py migrate
