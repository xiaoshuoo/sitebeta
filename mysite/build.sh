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

# Create superuser
echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'your-password-here')
END

# Create default categories
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
    # Проверяем существование категории по slug
    if not Category.objects.filter(slug=slug).exists():
        Category.objects.create(
            name=name,
            slug=slug,
            icon=cat_data['icon'],
            description=cat_data.get('description', '')
        )
        print(f"Created category: {name}")
    else:
        print(f"Category already exists: {name}")
END

# Run Django commands
python manage.py collectstatic --no-input --clear