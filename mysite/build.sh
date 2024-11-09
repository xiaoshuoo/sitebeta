#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p staticfiles
mkdir -p media

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate