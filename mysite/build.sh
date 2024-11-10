#!/bin/bash
# Exit on error
set -o errexit

# Установка виртуального окружения и зависимостей
python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Создание необходимых директорий
python create_static_dirs.py

# Экспорт переменной DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE=config.settings

# Сбор статических файлов
python manage.py collectstatic --no-input

# Применение миграций
python manage.py migrate