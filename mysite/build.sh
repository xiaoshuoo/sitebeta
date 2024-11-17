#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем необходимые директории
mkdir -p /opt/render/project/src/data/media/avatars
mkdir -p /opt/render/project/src/data/media/posts
mkdir -p /opt/render/project/src/data/media/covers
mkdir -p /opt/render/project/src/data/static

# Синхронизируем базу данных
python manage.py sync_database

# Применяем миграции
python manage.py migrate --noinput

# Создаем таблицу кэша
python manage.py createcachetable

# Создаем суперпользователя
python manage.py create_superuser

# Инициализируем базовые данные
python manage.py initialize_data

# Собираем статические файлы
python manage.py collectstatic --no-input
