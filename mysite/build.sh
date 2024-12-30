#!/usr/bin/env bash
# exit on error
set -o errexit

# Create necessary directories
mkdir -p staticfiles
mkdir -p static
mkdir -p media

# Install python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input --clear

# Apply database migrations
python manage.py migrate
