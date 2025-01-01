#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Creating necessary directories..."
# Create directories for static and media files
mkdir -p staticfiles
mkdir -p media
mkdir -p static/css

echo "Installing dependencies..."
# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Cleaning up old static files..."
# Clean up old static files
rm -rf staticfiles/*

echo "Ensuring CSS files exist..."
# Create CSS files if they don't exist
touch static/css/style.css
touch static/css/components.css
touch static/css/utilities.css
touch static/css/custom.css

# Copy Tailwind output if it exists
if [ -f "static/css/output.css" ]; then
    echo "Found Tailwind CSS output file"
else
    echo "Creating empty output.css"
    touch static/css/output.css
fi

echo "Collecting static files..."
# Collect static files
python manage.py collectstatic --no-input --clear

echo "Setting permissions..."
# Set permissions
chmod -R 755 staticfiles
chmod -R 755 media
chmod -R 755 static

echo "Running database migrations..."
# Apply database migrations
python manage.py migrate --no-input

echo "Build script completed!"
