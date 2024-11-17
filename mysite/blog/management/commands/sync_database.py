from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile, Post, Category, Tag, Comment
import psycopg2
from psycopg2.extras import DictCursor

class Command(BaseCommand):
    help = 'Синхронизация базы данных с PostgreSQL на Render'

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
            
            # Очищаем существующие данные
            Post.objects.all().delete()
            Category.objects.all().delete()
            Tag.objects.all().delete()
            Comment.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.all().delete()

            with conn.cursor(cursor_factory=DictCursor) as cursor:
                # Импортируем пользователей
                cursor.execute("SELECT * FROM auth_user")
                users = cursor.fetchall()
                for user_data in users:
                    User.objects.create(
                        id=user_data['id'],
                        username=user_data['username'],
                        email=user_data['email'],
                        password=user_data['password'],
                        is_superuser=user_data['is_superuser'],
                        is_staff=user_data['is_staff'],
                        is_active=user_data['is_active'],
                        date_joined=user_data['date_joined']
                    )

                # Импортируем профили
                cursor.execute("SELECT * FROM blog_profile")
                profiles = cursor.fetchall()
                for profile_data in profiles:
                    Profile.objects.create(
                        user_id=profile_data['user_id'],
                        avatar=profile_data['avatar'],
                        bio=profile_data['bio'],
                        location=profile_data['location'],
                        website=profile_data['website'],
                        occupation=profile_data['occupation'],
                        role=profile_data['role']
                    )

                # Импортируем категории
                cursor.execute("SELECT * FROM blog_category")
                categories = cursor.fetchall()
                for category_data in categories:
                    Category.objects.create(
                        id=category_data['id'],
                        name=category_data['name'],
                        slug=category_data['slug'],
                        description=category_data['description']
                    )

                # Импортируем посты
                cursor.execute("SELECT * FROM blog_post")
                posts = cursor.fetchall()
                for post_data in posts:
                    Post.objects.create(
                        id=post_data['id'],
                        title=post_data['title'],
                        slug=post_data['slug'],
                        content=post_data['content'],
                        created_at=post_data['created_at'],
                        updated_at=post_data['updated_at'],
                        author_id=post_data['author_id'],
                        category_id=post_data['category_id'],
                        is_published=post_data['is_published'],
                        views_count=post_data['views_count']
                    )

            conn.close()
            self.stdout.write(self.style.SUCCESS('Successfully synchronized database'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error synchronizing database: {str(e)}')) 