#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Создание директории для статических файлов
mkdir -p staticfiles

# Сбор статических файлов
python manage.py collectstatic --no-input

# Применение миграций
python manage.py migrate
