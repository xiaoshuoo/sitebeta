from django.core.management.base import BaseCommand
from django.core import serializers
from blog.models import Profile, Post, Category, Tag, Comment, PostView
from django.contrib.auth.models import User
import json
import psycopg2
from psycopg2.extras import Json

class Command(BaseCommand):
    help = 'Export data from local database to Render PostgreSQL'

    def handle(self, *args, **options):
        try:
            # Подключаемся к PostgreSQL на Render
            conn = psycopg2.connect(
                dbname='django_blog_7f9a',
                user='django_blog_7f9a_user',
                password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                port='5432',
                sslmode='require'
            )
            cursor = conn.cursor()

            # Экспортируем пользователей
            users = User.objects.all()
            for user in users:
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
                    user.username, user.email, user.password,
                    user.is_superuser, user.is_staff, user.is_active,
                    user.date_joined, user.first_name, user.last_name
                ))

            # Экспортируем профили
            profiles = Profile.objects.all()
            for profile in profiles:
                cursor.execute("""
                    INSERT INTO blog_profile (user_id, avatar, cover, bio, location, website, occupation, last_seen, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                    avatar=EXCLUDED.avatar,
                    cover=EXCLUDED.cover,
                    bio=EXCLUDED.bio,
                    location=EXCLUDED.location,
                    website=EXCLUDED.website,
                    occupation=EXCLUDED.occupation,
                    role=EXCLUDED.role
                """, (
                    profile.user_id, str(profile.avatar) if profile.avatar else None,
                    str(profile.cover) if profile.cover else None,
                    profile.bio, profile.location, profile.website,
                    profile.occupation, profile.last_seen, profile.role
                ))

            # Экспортируем категории
            categories = Category.objects.all()
            for category in categories:
                cursor.execute("""
                    INSERT INTO blog_category (name, slug, description, icon, created_at, updated_at, _posts_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                    name=EXCLUDED.name,
                    description=EXCLUDED.description,
                    icon=EXCLUDED.icon,
                    _posts_count=EXCLUDED._posts_count
                """, (
                    category.name, category.slug, category.description,
                    category.icon, category.created_at, category.updated_at,
                    category._posts_count
                ))

            # Экспортируем посты
            posts = Post.objects.all()
            for post in posts:
                cursor.execute("""
                    INSERT INTO blog_post (title, slug, content, created_at, updated_at, author_id, category_id, thumbnail, is_published, views_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                    title=EXCLUDED.title,
                    content=EXCLUDED.content,
                    updated_at=EXCLUDED.updated_at,
                    views_count=EXCLUDED.views_count
                """, (
                    post.title, post.slug, post.content,
                    post.created_at, post.updated_at, post.author_id,
                    post.category_id, str(post.thumbnail) if post.thumbnail else None,
                    post.is_published, post.views_count
                ))

            conn.commit()
            cursor.close()
            conn.close()

            self.stdout.write(self.style.SUCCESS('Successfully exported data to Render PostgreSQL'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error exporting data: {str(e)}')) 