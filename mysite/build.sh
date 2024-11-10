#!/usr/bin/env bash
# exit on error
set -o errexit

# Debug - показать текущую директорию и содержимое
echo "Current directory:"
pwd
echo "Directory contents:"
ls -la

# Найти requirements.txt
REQUIREMENTS_FILE=""
for possible_path in "./requirements.txt" "../requirements.txt" "mysite/requirements.txt" "*/requirements.txt"
do
    if [ -f "$possible_path" ]; then
        REQUIREMENTS_FILE=$possible_path
        echo "Found requirements.txt at: $REQUIREMENTS_FILE"
        break
    fi
done

if [ -z "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: requirements.txt not found!"
    exit 1
fi

# Install dependencies
echo "Installing dependencies from $REQUIREMENTS_FILE"
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# Create necessary directories if script exists
if [ -f "create_static_dirs.py" ]; then
    python create_static_dirs.py
fi

# Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate