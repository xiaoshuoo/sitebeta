#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем необходимые директории
mkdir -p static/css static/js media/avatars media/posts media/covers

# Копируем CSS файлы
cp -r static/css/* staticfiles/css/ || true

# Применяем миграции
python manage.py migrate --noinput

# Создаем суперпользователя
python manage.py create_superuser

# Собираем статические файлы без пост-обработки
python manage.py collectstatic --no-input --clear --no-post-process
