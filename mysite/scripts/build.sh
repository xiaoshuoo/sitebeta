#!/usr/bin/env bash

# Выход при любой ошибке
set -o errexit

# Обновляем pip
python -m pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt

# Собираем статические файлы
python manage.py collectstatic --no-input

# Применяем миграции
python manage.py migrate

# Создаем бэкап перед деплоем
python scripts/backup.py 