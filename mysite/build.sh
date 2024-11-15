#!/usr/bin/env bash
set -o errexit

# Создаем директорию для базы данных
mkdir -p /opt/render/project/src/mysite

# Если мы на Render и база существует в корне, перемещаем её
if [ "$RENDER" = "true" ] && [ -f db.sqlite3 ]; then
    mv db.sqlite3 /opt/render/project/src/mysite/
fi

# Установка зависимостей
pip install -r requirements.txt

# Применяем миграции
python manage.py migrate

# Собираем статические файлы
python manage.py collectstatic --no-input
