#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Удаляем старые миграции
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Создаем новые миграции
python manage.py makemigrations

# Применяем миграции с флагом --force
python manage.py migrate --force

# Создаем суперпользователя
python manage.py create_superuser

# Собираем статические файлы
python manage.py collectstatic --no-input

# Экспортируем данные из SQLite в PostgreSQL
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
python manage.py loaddata data.json
