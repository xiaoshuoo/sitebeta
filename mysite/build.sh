#!/bin/bash
set -o errexit

cd mysite

# Установка зависимостей
python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Создание необходимых директорий
python create_static_dirs.py

# Сбор статических файлов
python manage.py collectstatic --no-input

# Применение миграций
python manage.py migrate