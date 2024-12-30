#!/usr/bin/env bash
# exit on error
set -o errexit

# Create necessary directories with proper permissions
mkdir -p staticfiles
mkdir -p static
mkdir -p media
chmod -R 755 staticfiles
chmod -R 755 static
chmod -R 755 media

# Install python dependencies
pip install -r requirements.txt

# Clean and collect static files
rm -rf staticfiles/*
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
