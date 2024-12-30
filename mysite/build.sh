#!/usr/bin/env bash
# exit on error
set -o errexit

# Добавляем текущую директорию в PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Создаем необходимые директории
mkdir -p staticfiles
mkdir -p media

# Установка зависимостей
pip install -r requirements.txt

# Сбор статических файлов
python manage.py collectstatic --no-input

# Применение миграций
python manage.py migrate
