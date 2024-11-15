#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Ждем доступности базы данных
echo "Waiting for PostgreSQL..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_superuser
