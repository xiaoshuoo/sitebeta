from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile, Post, Category, Tag, Comment, PostView, InviteCode, PageSettings
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Миграция данных из SQLite в PostgreSQL'

    def handle(self, *args, **options):
        try:
            # Подключаемся к SQLite
            sqlite_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            sqlite_conn = sqlite3.connect(sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row

            # Подключаемся к PostgreSQL
            pg_conn = psycopg2.connect(
                dbname='django_blog_7f9a',
                user='django_blog_7f9a_user',
                password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                port='5432',
                sslmode='require'
            )
            pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)

            # Мигрируем пользователей
            sqlite_cursor = sqlite_conn.execute('SELECT * FROM auth_user')
            for user in sqlite_cursor.fetchall():
                pg_cursor.execute("""
                    INSERT INTO auth_user (
                        id, username, email, password, is_superuser, 
                        is_staff, is_active, date_joined, first_name, last_name
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        username = EXCLUDED.username,
                        email = EXCLUDED.email
                """, (
                    user['id'], user['username'], user['email'], user['password'],
                    bool(user['is_superuser']), bool(user['is_staff']), 
                    bool(user['is_active']), user['date_joined'],
                    user['first_name'], user['last_name']
                ))

            # Мигрируем профили
            sqlite_cursor = sqlite_conn.execute('SELECT * FROM blog_profile')
            for profile in sqlite_cursor.fetchall():
                pg_cursor.execute("""
                    INSERT INTO blog_profile (
                        id, user_id, avatar, cover, bio, location,
                        website, occupation, last_seen, role
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        avatar = EXCLUDED.avatar,
                        cover = EXCLUDED.cover,
                        bio = EXCLUDED.bio
                """, (
                    profile['id'], profile['user_id'], profile['avatar'],
                    profile['cover'], profile['bio'], profile['location'],
                    profile['website'], profile['occupation'],
                    profile['last_seen'], profile['role']
                ))

            # Мигрируем категории
            sqlite_cursor = sqlite_conn.execute('SELECT * FROM blog_category')
            for category in sqlite_cursor.fetchall():
                pg_cursor.execute("""
                    INSERT INTO blog_category (
                        id, name, slug, description, icon,
                        created_at, updated_at, posts_count
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description
                """, (
                    category['id'], category['name'], category['slug'],
                    category['description'], category['icon'],
                    category['created_at'], category['updated_at'],
                    category['_posts_count']
                ))

            # Мигрируем посты
            sqlite_cursor = sqlite_conn.execute('SELECT * FROM blog_post')
            for post in sqlite_cursor.fetchall():
                pg_cursor.execute("""
                    INSERT INTO blog_post (
                        id, title, slug, content, created_at,
                        updated_at, author_id, category_id,
                        thumbnail, is_published, views_count
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        content = EXCLUDED.content
                """, (
                    post['id'], post['title'], post['slug'], post['content'],
                    post['created_at'], post['updated_at'], post['author_id'],
                    post['category_id'], post['thumbnail'],
                    bool(post['is_published']), post['views_count']
                ))

            # Фиксируем изменения
            pg_conn.commit()

            # Закрываем соединения
            sqlite_conn.close()
            pg_conn.close()

            self.stdout.write(self.style.SUCCESS('Миграция данных успешно завершена'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при миграции: {str(e)}')) 