#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
python create_static_dirs.py

# Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate