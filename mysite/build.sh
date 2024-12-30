#!/usr/bin/env bash
# exit on error
set -o errexit

# Create directories
mkdir -p /opt/render/project/src/staticfiles
mkdir -p /opt/render/project/src/media/avatars
mkdir -p /opt/render/project/src/media/posts
mkdir -p /opt/render/project/src/media/covers
mkdir -p /opt/render/project/src/media/thumbnails

# Set permissions
chmod -R 777 /opt/render/project/src/media
chmod -R 777 /opt/render/project/src/staticfiles

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create static directory if it doesn't exist
python -c "import os; os.makedirs('static', exist_ok=True)"

# Clean up old static files
rm -rf /opt/render/project/src/staticfiles/*

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Print success message
echo "Build completed successfully"

# Function to check if service is healthy
check_service() {
    for i in {1..30}; do
        if curl -f "http://localhost:$PORT/health/" >/dev/null 2>&1 || curl -f "http://0.0.0.0:$PORT/health/" >/dev/null 2>&1; then
            echo "Service is up!"
            return 0
        fi
        echo "Waiting for service to start... ($i/30)"
        sleep 2
    done
    return 1
}

# Start gunicorn in background
gunicorn config.wsgi:application \
    --bind=0.0.0.0:$PORT \
    --config=gunicorn.conf.py &

# Wait for service to be healthy
if check_service; then
    # Keep the script running
    wait
else
    echo "Service failed to start"
    exit 1
fi
