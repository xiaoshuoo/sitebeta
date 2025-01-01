#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Creating necessary directories..."
# Create directories for static and media files
mkdir -p staticfiles
mkdir -p media
mkdir -p static

echo "Installing dependencies..."
# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Cleaning up old static files..."
# Clean up old static files
rm -rf staticfiles/*

echo "Collecting static files..."
# Collect static files
python manage.py collectstatic --no-input --clear

echo "Setting permissions..."
# Set permissions
chmod -R 755 staticfiles
chmod -R 755 media
chmod -R 755 static

echo "Copying static files..."
# Ensure static files are in place
cp -r static/* staticfiles/ 2>/dev/null || true

echo "Running database migrations..."
# Apply database migrations
python manage.py migrate --no-input

echo "Build script completed!"
