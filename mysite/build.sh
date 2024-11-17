#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем необходимые директории
mkdir -p /opt/render/project/src/data/media/avatars
mkdir -p /opt/render/project/src/data/media/posts
mkdir -p /opt/render/project/src/data/media/covers
mkdir -p /opt/render/project/src/data/static

# Проверяем подключение к базе данных и данные
python -c "
import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(
    dbname='django_blog_7f9a',
    user='django_blog_7f9a_user',
    password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
    host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
    port='5432',
    sslmode='require'
)

with conn.cursor(cursor_factory=DictCursor) as cursor:
    # Проверяем версию PostgreSQL
    cursor.execute('SELECT version();')
    print('Database version:', cursor.fetchone()[0])
    
    # Проверяем существующие таблицы
    cursor.execute('''
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    ''')
    tables = cursor.fetchall()
    print('\nExisting tables:')
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
        count = cursor.fetchone()[0]
        print(f'- {table[0]}: {count} records')

conn.close()
print('\nDatabase connection and data check completed successfully')
"

# Применяем миграции
python manage.py migrate --noinput

# Создаем таблицу кэша
python manage.py createcachetable

# Создаем суперпользователя
python manage.py create_superuser

# Собираем статические файлы
python manage.py collectstatic --no-input
