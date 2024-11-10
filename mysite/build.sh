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
mkdir -p staticfiles
mkdir -p media

# Handle migrations
echo "Handling migrations..."
python manage.py makemigrations blog
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print('Superuser created successfully')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f'Failed to create superuser: {str(e)}')
END

# Create initial invite code
echo "Creating initial invite code..."
python manage.py shell << END
from blog.models import InviteCode, Category, Post
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(username='admin')

# Create invite code
try:
    if not InviteCode.objects.filter(code='ADMIN123').exists():
        InviteCode.objects.create(
            code='ADMIN123',
            created_by=admin,
            is_active=True
        )
        print('Initial invite code created successfully')
    else:
        print('Initial invite code already exists')
except Exception as e:
    print(f'Failed to create invite code: {str(e)}')

# Create test category
try:
    category, created = Category.objects.get_or_create(
        name='Тестовая категория',
        defaults={
            'description': 'Тестовая категория для демонстрации',
            'icon': 'fa-flask'
        }
    )
    print('Category created successfully' if created else 'Category already exists')
except Exception as e:
    print(f'Failed to create category: {str(e)}')

# Create test post
try:
    if not Post.objects.filter(title='Добро пожаловать!').exists():
        Post.objects.create(
            title='Добро пожаловать!',
            content='Это тестовый пост для демонстрации функционала блога.',
            author=admin,
            category=category,
            is_published=True
        )
        print('Test post created successfully')
    else:
        print('Test post already exists')
except Exception as e:
    print(f'Failed to create test post: {str(e)}')
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Копируем существующие статические файлы поверх собранных
echo "Copying custom static files..."
cp -rv static/* staticfiles/ || echo "No static files to copy"

# Set permissions
echo "Setting permissions..."
chmod -R 755 staticfiles media

# Debug - показать финальное содержимое staticfiles
echo "Final staticfiles contents:"
ls -la staticfiles/