#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Применяем миграции
python manage.py migrate --noinput

# Синхронизируем базу данных
python manage.py sync_database

# Создаем суперпользователя
python manage.py create_superuser

# Собираем статические файлы
python manage.py collectstatic --no-input
