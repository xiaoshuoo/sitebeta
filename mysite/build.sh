#!/usr/bin/env bash
# exit on error
set -o errexit

# Создаем директории для постоянного хранения медиа файлов
mkdir -p /opt/render/project/src/media/avatars
mkdir -p /opt/render/project/src/media/posts
mkdir -p /opt/render/project/src/media/covers
mkdir -p /opt/render/project/src/media/thumbnails

# Устанавливаем права на запись для всех директорий
chmod -R 777 /opt/render/project/src/media

# Создаем символическую ссылку для доступа к медиа файлам
ln -sf /opt/render/project/src/media /opt/render/project/src/staticfiles/media

python -m pip install --upgrade pip
pip install -r requirements.txt

# Собираем статические файлы
python manage.py collectstatic --noinput

# Применяем миграции
python manage.py migrate --noinput


# Создаем таблицу кэша
python manage.py createcachetable

# Создаем суперпользователя
python manage.py create_superuser

# Синхронизируем базу данных
python manage.py sync_database


# Проверяем подключение к базе данных
python -c "
import psycopg2
conn = psycopg2.connect(
    dbname='django_blog_7f9a',
    user='django_blog_7f9a_user',
    password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
    host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
    port='5432',
    sslmode='require'
)
cursor = conn.cursor()
cursor.execute('SELECT version();')
print('Database connection successful:', cursor.fetchone()[0])
cursor.close()
conn.close()
"

# Запускаем gunicorn
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT --workers=4 --access-logfile=- --error-logfile=-