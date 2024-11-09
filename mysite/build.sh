#!/bin/bash
# Exit on error
set -o errexit

# Create virtual environment and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
python create_static_dirs.py

# Collect static files
python manage.py collectstatic --no-input

# Apply migrations
python manage.py migrate