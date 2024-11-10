#!/usr/bin/env bash
# exit on error
set -o errexit

# Debug - показать текущую директорию и содержимое
echo "Current directory:"
pwd
echo "Directory contents:"
ls -la

# Перейти в директорию mysite, если мы не в ней
if [ ! -f "manage.py" ] && [ -d "mysite" ]; then
    echo "Changing to mysite directory"
    cd mysite
    echo "New directory:"
    pwd
    echo "New directory contents:"
    ls -la
fi

# Set up Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "PYTHONPATH: $PYTHONPATH"

# Install dependencies
echo "Installing dependencies from requirements.txt"
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories if script exists
if [ -f "create_static_dirs.py" ]; then
    python create_static_dirs.py
fi

# Reset migrations
echo "Resetting migrations..."
find blog/migrations -type f -name "*.py" ! -name "__init__.py" -delete
python manage.py makemigrations blog

# Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate --run-syncdb