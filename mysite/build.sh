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

# Safely handle migrations
echo "Handling migrations..."
mkdir -p blog/migrations
touch blog/migrations/__init__.py

# Remove old migrations using Python
python << END
import os
import glob

migrations_dir = 'blog/migrations'
for file in glob.glob(os.path.join(migrations_dir, '*.py')):
    if os.path.basename(file) != '__init__.py':
        os.remove(file)
END

# Create fresh migrations
python manage.py makemigrations blog

# Apply migrations with fake initial
python manage.py migrate --fake-initial

# Run Django commands
python manage.py collectstatic --no-input