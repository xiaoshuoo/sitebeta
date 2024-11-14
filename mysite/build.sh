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
mkdir -p static staticfiles media/uploads
chmod -R 755 static staticfiles media

# Copy static files
echo "Copying static files..."
if [ -d "static_source" ]; then
    cp -r static_source/* static/
fi

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

# Create initial data
echo "Creating initial data..."
python manage.py shell << END
from blog.models import Category, Post, InviteCode
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(username='admin')

# Create categories
categories_data = [
    {'name': 'Технологии', 'icon': 'fa-laptop-code', 'description': 'Технологические новости и обзоры'},
    {'name': 'Путешествия', 'icon': 'fa-plane', 'description': 'Путешествия и приключения'},
    {'name': 'Lifestyle', 'icon': 'fa-heart', 'description': 'Образ жизни и саморазвитие'}
]

for cat_data in categories_data:
    Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={
            'icon': cat_data['icon'],
            'description': cat_data['description']
        }
    )

# Create invite code
if not InviteCode.objects.filter(code='ADMIN123').exists():
    InviteCode.objects.create(
        code='ADMIN123',
        created_by=admin,
        is_active=True
    )

# Create welcome post
tech_category = Category.objects.get(name='Технологии')
if not Post.objects.filter(title='Добро пожаловать!').exists():
    Post.objects.create(
        title='Добро пожаловать!',
        content='<h2>Добро пожаловать в наш блог!</h2><p>Здесь вы найдете интересные статьи на различные темы.</p>',
        author=admin,
        category=tech_category,
        is_published=True
    )
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Set permissions
echo "Setting permissions..."
chmod -R 755 staticfiles media

# Debug - показать финальное содержимое
echo "Final directory contents:"
ls -la
