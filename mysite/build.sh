#!/usr/bin/env bash
# exit on error
set -o errexit

# Создаем директории для медиа файлов
mkdir -p media/avatars
mkdir -p media/posts
mkdir -p media/covers
mkdir -p media/thumbnails

# Устанавливаем права на запись
chmod -R 777 media

# Обновляем pip и устанавливаем зависимости
python -m pip install --upgrade pip
pip install -r requirements.txt

# Экспортируем переменные окружения из .env файла
export $(cat .env | xargs)

# Собираем статические файлы и выполняем миграции
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Создаем необходимые директории
python manage.py check_media

# Проверяем и восстанавливаем права доступа
chmod -R 777 media

# Запускаем gunicorn
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT --workers=4
