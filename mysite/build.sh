#!/usr/bin/env bash
# exit on error
set -o errexit

# Создаем необходимые директории
mkdir -p staticfiles
mkdir -p media

# Обновляем pip и устанавливаем зависимости
python -m pip install --upgrade pip
pip install -r requirements.txt

# Собираем статические файлы
python manage.py collectstatic --no-input

# Применяем миграции
python manage.py migrate