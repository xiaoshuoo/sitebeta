#!/bin/bash
# Exit on error
set -o errexit

# Debug: Print current directory and list files
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Install python dependencies
pip install -r requirements.txt

# Create static directory if it doesn't exist
python create_static_dirs.py

# Collect static files
python manage.py collectstatic --no-input

# Add the project root to PYTHONPATH
export PYTHONPATH="/opt/render/project/src:$PYTHONPATH"

# Debug: Print final directory structure
echo "Final directory structure:"
ls -R