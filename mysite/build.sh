#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка PostgreSQL клиента
apt-get update
apt-get install -y postgresql-client

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_superuser
