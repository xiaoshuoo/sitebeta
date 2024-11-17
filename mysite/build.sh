#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем необходимые директории
mkdir -p static/css static/js media/avatars media/posts media/covers

# Копируем CSS файлы
cp -r static/css/* staticfiles/css/ || true

# Применяем миграции
python manage.py migrate --noinput

# Создаем таблицу кэша
python manage.py createcachetable

# Создаем суперпользователя
python manage.py create_superuser

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

# Собираем статические файлы без пост-обработки
DISABLE_COLLECTSTATIC=1 python manage.py collectstatic --no-input --clear --no-post-process

# Копируем tailwind CSS файлы
mkdir -p staticfiles/css/tailwindcss
cp static/css/tailwindcss/* staticfiles/css/tailwindcss/ || true
