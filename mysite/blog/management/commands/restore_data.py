from django.core.management.base import BaseCommand
import json
import os
from django.contrib.auth.models import User
from blog.models import Profile, Post, Category, Tag, Comment, PostView, Title, TextTemplate
from django.utils.text import slugify
from datetime import datetime

class Command(BaseCommand):
    help = 'Восстановление данных из бэкапа'

    def handle(self, *args, **options):
        try:
            # Находим последний файл бэкапа
            backup_files = [f for f in os.listdir('.') if f.startswith('backup_') and f.endswith('.json')]
            if not backup_files:
                self.stdout.write(self.style.ERROR('Файлы бэкапа не найдены'))
                return
            
            latest_backup = max(backup_files)  # Получаем самый новый файл
            self.stdout.write(f'Используется файл бэкапа: {latest_backup}')

            # Загружаем данные из бэкапа
            with open(latest_backup, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Восстанавливаем пользователей
            for user_data in data.get('auth_user', []):
                if not User.objects.filter(username=user_data['username']).exists():
                    try:
                        User.objects.create(
                            id=user_data['id'],
                            username=user_data['username'],
                            email=user_data['email'],
                            password=user_data['password'],
                            is_superuser=user_data['is_superuser'],
                            is_staff=user_data['is_staff'],
                            is_active=user_data['is_active'],
                            date_joined=datetime.fromisoformat(user_data['date_joined'].replace('Z', '+00:00'))
                        )
                        self.stdout.write(f'Восстановлен пользователь: {user_data["username"]}')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Ошибка при восстановлении пользователя {user_data["username"]}: {str(e)}'))

            # Восстанавливаем профили
            for profile_data in data.get('blog_profile', []):
                try:
                    user = User.objects.get(id=profile_data['user_id'])
                    if not Profile.objects.filter(user=user).exists():
                        Profile.objects.create(
                            id=profile_data['id'],
                            user=user,
                            avatar=profile_data.get('avatar'),
                            bio=profile_data.get('bio'),
                            location=profile_data.get('location'),
                            website=profile_data.get('website'),
                            occupation=profile_data.get('occupation'),
                            role=profile_data.get('role', 'user')
                        )
                        self.stdout.write(f'Восстановлен профиль для: {user.username}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Ошибка при восстановлении профиля: {str(e)}'))

            # Восстанавливаем категории
            for category_data in data.get('blog_category', []):
                if not Category.objects.filter(slug=category_data['slug']).exists():
                    try:
                        Category.objects.create(
                            id=category_data['id'],
                            name=category_data['name'],
                            slug=category_data['slug'],
                            description=category_data.get('description', ''),
                            icon=category_data.get('icon', 'fa-folder')
                        )
                        self.stdout.write(f'Восстановлена категория: {category_data["name"]}')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Ошибка при восстановлении категории: {str(e)}'))

            # Восстанавливаем посты
            for post_data in data.get('blog_post', []):
                if not Post.objects.filter(slug=post_data['slug']).exists():
                    try:
                        author = User.objects.get(id=post_data['author_id'])
                        category = Category.objects.get(id=post_data['category_id']) if post_data.get('category_id') else None
                        Post.objects.create(
                            id=post_data['id'],
                            title=post_data['title'],
                            slug=post_data['slug'],
                            content=post_data['content'],
                            created_at=datetime.fromisoformat(post_data['created_at'].replace('Z', '+00:00')),
                            updated_at=datetime.fromisoformat(post_data['updated_at'].replace('Z', '+00:00')),
                            author=author,
                            category=category,
                            thumbnail=post_data.get('thumbnail'),
                            is_published=post_data['is_published'],
                            views_count=post_data['views_count']
                        )
                        self.stdout.write(f'Восстановлен пост: {post_data["title"]}')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Ошибка при восстановлении поста: {str(e)}'))

            self.stdout.write(self.style.SUCCESS('Данные успешно восстановлены'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при восстановлении данных: {str(e)}')) 