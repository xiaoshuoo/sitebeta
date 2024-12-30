#!/usr/bin/env bash
# exit on error
set -o errexit

# Создание необходимых директорий
mkdir -p static
mkdir -p media
mkdir -p staticfiles

# Установка зависимостей
pip install -r requirements.txt

# Сбор статических файлов
python manage.py collectstatic --no-input

# Применение миграций
python manage.py migrate
