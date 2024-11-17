#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Очищаем старые миграции
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Создаем новые миграции
python manage.py makemigrations auth
python manage.py makemigrations admin
python manage.py makemigrations contenttypes
python manage.py makemigrations sessions
python manage.py makemigrations blog

# Применяем миграции
python manage.py migrate auth --noinput
python manage.py migrate admin --noinput
python manage.py migrate contenttypes --noinput
python manage.py migrate sessions --noinput
python manage.py migrate blog --noinput

# Создаем суперпользователя
python manage.py create_superuser

# Собираем статические файлы
python manage.py collectstatic --no-input

# Создаем таблицу для кэша
python manage.py createcachetable

# Проверяем структуру базы данных
python manage.py check --database default

# Создаем необходимые директории
mkdir -p media/avatars media/posts media/covers backups
