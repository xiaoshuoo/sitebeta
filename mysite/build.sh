#!/usr/bin/env bash
# exit on error
set -o errexit

# Создаем директории для медиа файлов
mkdir -p /opt/render/project/src/media/avatars
mkdir -p /opt/render/project/src/media/posts
mkdir -p /opt/render/project/src/media/covers
mkdir -p /opt/render/project/src/media/thumbnails

# Устанавливаем права на запись
chmod -R 777 /opt/render/project/src/media

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Запускаем gunicorn
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT --workers=4

# Создаем необходимые директории
python manage.py check_media

# Проверяем и восстанавливаем права доступа
chmod -R 777 /opt/render/project/src/media
