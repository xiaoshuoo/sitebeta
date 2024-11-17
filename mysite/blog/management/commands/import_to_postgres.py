from django.core.management.base import BaseCommand
import json
import psycopg2
from psycopg2.extras import Json
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from JSON to PostgreSQL on Render'

    def handle(self, *args, **options):
        try:
            # Загружаем данные из JSON
            with open('local_data_export.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Подключаемся к PostgreSQL
            conn = psycopg2.connect(
                dbname='django_blog_7f9a',
                user='django_blog_7f9a_user',
                password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                port='5432',
                sslmode='require'
            )
            cursor = conn.cursor()

            # Создаем необходимые таблицы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(150) UNIQUE NOT NULL,
                    email VARCHAR(254),
                    password VARCHAR(128) NOT NULL,
                    first_name VARCHAR(150),
                    last_name VARCHAR(150),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_staff BOOLEAN DEFAULT FALSE,
                    is_superuser BOOLEAN DEFAULT FALSE,
                    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP WITH TIME ZONE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blog_profile (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
                    avatar VARCHAR(100),
                    cover VARCHAR(100),
                    bio TEXT,
                    location VARCHAR(100),
                    website VARCHAR(200),
                    occupation VARCHAR(100),
                    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    role VARCHAR(20) DEFAULT 'user'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blog_category (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    slug VARCHAR(100) UNIQUE,
                    description TEXT,
                    icon VARCHAR(50) DEFAULT 'fa-folder',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    _posts_count INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blog_post (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    slug VARCHAR(255) UNIQUE,
                    content TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    author_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
                    category_id INTEGER REFERENCES blog_category(id) ON DELETE SET NULL,
                    thumbnail VARCHAR(100),
                    is_published BOOLEAN DEFAULT FALSE,
                    views_count INTEGER DEFAULT 0
                )
            """)

            # Импортируем пользователей
            for user in data['users']:
                cursor.execute("""
                    INSERT INTO auth_user (username, email, password, is_superuser, is_staff, is_active, date_joined, first_name, last_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (username) DO UPDATE SET
                    email=EXCLUDED.email,
                    password=EXCLUDED.password,
                    is_superuser=EXCLUDED.is_superuser,
                    is_staff=EXCLUDED.is_staff,
                    is_active=EXCLUDED.is_active
                """, (
                    user['username'], user['email'], user['password'],
                    user['is_superuser'], user['is_staff'], user['is_active'],
                    user['date_joined'], user['first_name'], user['last_name']
                ))

            # Импортируем профили
            for profile in data['profiles']:
                cursor.execute("""
                    INSERT INTO blog_profile (user_id, avatar, cover, bio, location, website, occupation, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                    avatar=EXCLUDED.avatar,
                    cover=EXCLUDED.cover,
                    bio=EXCLUDED.bio,
                    location=EXCLUDED.location,
                    website=EXCLUDED.website,
                    occupation=EXCLUDED.occupation,
                    role=EXCLUDED.role
                """, (
                    profile['user_id'], profile['avatar'], profile['cover'],
                    profile['bio'], profile['location'], profile['website'],
                    profile['occupation'], profile['role']
                ))

            # Импортируем категории
            for category in data['categories']:
                cursor.execute("""
                    INSERT INTO blog_category (name, slug, description, icon, created_at, updated_at, _posts_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                    name=EXCLUDED.name,
                    description=EXCLUDED.description,
                    icon=EXCLUDED.icon,
                    _posts_count=EXCLUDED._posts_count
                """, (
                    category['name'], category['slug'], category['description'],
                    category['icon'], category['created_at'], category['updated_at'],
                    category['_posts_count']
                ))

            # Импортируем посты
            for post in data['posts']:
                cursor.execute("""
                    INSERT INTO blog_post (title, slug, content, created_at, updated_at, author_id, category_id, thumbnail, is_published, views_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                    title=EXCLUDED.title,
                    content=EXCLUDED.content,
                    updated_at=EXCLUDED.updated_at,
                    views_count=EXCLUDED.views_count
                """, (
                    post['title'], post['slug'], post['content'],
                    post['created_at'], post['updated_at'], post['author_id'],
                    post['category_id'], post['thumbnail'], post['is_published'],
                    post['views_count']
                ))

            conn.commit()
            cursor.close()
            conn.close()

            self.stdout.write(self.style.SUCCESS('Successfully imported data to PostgreSQL'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}')) 