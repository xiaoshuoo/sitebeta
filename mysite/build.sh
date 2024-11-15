#!/usr/bin/env bash
# exit on error
set -o errexit

# Создаем директорию для базы данных
mkdir -p /opt/render/project/src/data

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_superuser
