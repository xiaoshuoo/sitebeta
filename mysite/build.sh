#!/usr/bin/env bash
# exit on error
set -o errexit

# Create necessary directories
mkdir -p staticfiles
mkdir -p static/css
mkdir -p static/js
mkdir -p media

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Clean up old static files
rm -rf staticfiles/*

# Collect static files
python manage.py collectstatic --no-input --clear

# Run migrations
python manage.py migrate
