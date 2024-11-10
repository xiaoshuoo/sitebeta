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
fi

# Set up Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Install dependencies
echo "Installing dependencies from requirements.txt"
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p static staticfiles media
mkdir -p static/css static/js static/img

# Copy all static files from your local directory
echo "Copying static files..."
cat > static/css/style.css << 'END'
/* Скопируйте сюда содержимое вашего style.css */
:root {
    --primary-color: #8B5CF6;
    --secondary-color: #4F46E5;
    --background-color: #1A1625;
    --surface-color: #2D2A3D;
    --text-color: #E2E8F0;
    --text-muted: #94A3B8;
    --border-color: #4B5563;
}

body {
    background-color: var(--background-color);
    color: var(--text-color);
    font-family: 'Inter', sans-serif;
    margin: 0;
    padding: 0;
}

/* Добавьте остальные стили из вашего файла */
END

# Create necessary directories if script exists
if [ -f "create_static_dirs.py" ]; then
    python create_static_dirs.py
fi

# Handle migrations
echo "Handling migrations..."
python manage.py makemigrations blog
python manage.py migrate --fake-initial

# Create superuser
echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'your-password-here')
END

# Create categories
echo "Creating default categories..."
python manage.py shell << END
from blog.models import Category
from django.utils.text import slugify

categories = [
    {'name': 'Технологии', 'icon': 'fa-laptop-code', 'description': 'Технологические новости и обзоры'},
    {'name': 'Путешествия', 'icon': 'fa-plane', 'description': 'Путешествия и приключения'},
    {'name': 'Lifestyle', 'icon': 'fa-heart', 'description': 'Образ жизни и саморазвитие'}
]

for cat_data in categories:
    name = cat_data['name']
    slug = slugify(name)
    if not Category.objects.filter(slug=slug).exists():
        Category.objects.create(
            name=name,
            slug=slug,
            icon=cat_data['icon'],
            description=cat_data.get('description', '')
        )
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Set permissions
echo "Setting permissions..."
chmod -R 755 static staticfiles media