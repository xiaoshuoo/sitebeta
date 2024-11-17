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

# Создаем таблицу для кэша
python manage.py createcachetable

# Собираем статические файлы без сжатия и манифеста
DISABLE_COLLECTSTATIC=1 python manage.py collectstatic --noinput --clear --no-post-process
