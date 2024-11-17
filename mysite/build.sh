#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем необходимые директории
mkdir -p static/css static/js static/tinymce media/avatars media/posts media/covers

# Применяем миграции
python manage.py migrate --noinput

# Создаем суперпользователя
python manage.py create_superuser

# Создаем таблицу для кэша
python manage.py createcachetable

# Собираем статические файлы
python manage.py collectstatic --no-input --clear --ignore=*.scss --ignore=*.sass --ignore=*.less
