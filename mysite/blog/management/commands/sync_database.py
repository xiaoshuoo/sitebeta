from django.core.management.base import BaseCommand
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Command(BaseCommand):
    help = 'Синхронизация и создание таблиц в PostgreSQL'

    def handle(self, *args, **options):
        try:
            # Подключаемся к PostgreSQL
            conn = psycopg2.connect(
                dbname='django_blog_7f9a',
                user='django_blog_7f9a_user',
                password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                port='5432',
                sslmode='require'
            )
            
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Создаем таблицы
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
                );

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
                );

                CREATE TABLE IF NOT EXISTS blog_category (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    slug VARCHAR(100) UNIQUE,
                    description TEXT,
                    icon VARCHAR(50) DEFAULT 'fa-folder',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    posts_count INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS blog_tag (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    slug VARCHAR(100) UNIQUE
                );

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
                );

                CREATE TABLE IF NOT EXISTS blog_post_tags (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER REFERENCES blog_post(id) ON DELETE CASCADE,
                    tag_id INTEGER REFERENCES blog_tag(id) ON DELETE CASCADE,
                    UNIQUE(post_id, tag_id)
                );

                CREATE TABLE IF NOT EXISTS blog_comment (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER REFERENCES blog_post(id) ON DELETE CASCADE,
                    author_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
                    content TEXT,
                    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS blog_postview (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER REFERENCES blog_post(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
                    session_key VARCHAR(40),
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(post_id, user_id),
                    UNIQUE(post_id, session_key)
                );

                CREATE TABLE IF NOT EXISTS blog_invitecode (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(8) UNIQUE,
                    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    used_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
                    used_at TIMESTAMP WITH TIME ZONE
                );

                CREATE TABLE IF NOT EXISTS blog_pagesettings (
                    id SERIAL PRIMARY KEY,
                    page_name VARCHAR(100) UNIQUE,
                    is_active BOOLEAN DEFAULT TRUE,
                    disabled_message TEXT DEFAULT 'Страница временно недоступна',
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL
                );
            """)

            # Проверяем подключение и созданные таблицы
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS('Созданы следующие таблицы:'))
            for table in tables:
                self.stdout.write(f"- {table[0]}")

            cursor.close()
            conn.close()

            self.stdout.write(self.style.SUCCESS('База данных успешно синхронизирована'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при синхронизации базы данных: {str(e)}')) 