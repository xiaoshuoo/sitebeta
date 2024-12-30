#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p staticfiles
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

# Clean up old static files
rm -rf staticfiles/*

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
