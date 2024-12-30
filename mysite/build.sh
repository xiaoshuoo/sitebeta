#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Creating directories..."
mkdir -p staticfiles
mkdir -p static
mkdir -p media

echo "Setting permissions..."
chmod -R 755 staticfiles
chmod -R 755 static
chmod -R 755 media

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running migrations..."
python manage.py migrate
