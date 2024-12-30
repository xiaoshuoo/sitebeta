from django.core.management.base import BaseCommand
import os
import shutil
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Синхронизация медиа файлов между локальной версией и сервером'

    def handle(self, *args, **options):
        # URL вашего сайта на Render
        RENDER_URL = 'https://sity-lvo8.onrender.com'
        
        # Локальная директория media
        local_media = os.path.join(settings.BASE_DIR, 'media')
        
        # Создаем директории если их нет
        for dir_name in ['avatars', 'covers', 'thumbnails', 'posts']:
            os.makedirs(os.path.join(local_media, dir_name), exist_ok=True)

        # Получаем список всех файлов из базы данных
        from blog.models import Profile, Post
        
        # Синхронизируем аватары
        for profile in Profile.objects.all():
            if profile.avatar:
                file_url = f"{RENDER_URL}{profile.avatar.url}"
                local_path = os.path.join(local_media, 'avatars', os.path.basename(profile.avatar.name))
                
                try:
                    response = requests.get(file_url, stream=True)
                    if response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            shutil.copyfileobj(response.raw, f)
                        self.stdout.write(f'Скачан аватар: {local_path}')
                except Exception as e:
                    self.stdout.write(f'Ошибка при скачивании аватара: {e}')

            if profile.cover:
                file_url = f"{RENDER_URL}{profile.cover.url}"
                local_path = os.path.join(local_media, 'covers', os.path.basename(profile.cover.name))
                
                try:
                    response = requests.get(file_url, stream=True)
                    if response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            shutil.copyfileobj(response.raw, f)
                        self.stdout.write(f'Скачана обложка: {local_path}')
                except Exception as e:
                    self.stdout.write(f'Ошибка при скачивании обложки: {e}')

        # Синхронизируем миниатюры постов
        for post in Post.objects.all():
            if post.thumbnail:
                file_url = f"{RENDER_URL}{post.thumbnail.url}"
                local_path = os.path.join(local_media, 'thumbnails', os.path.basename(post.thumbnail.name))
                
                try:
                    response = requests.get(file_url, stream=True)
                    if response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            shutil.copyfileobj(response.raw, f)
                        self.stdout.write(f'Скачана миниатюра: {local_path}')
                except Exception as e:
                    self.stdout.write(f'Ошибка при скачивании миниатюры: {e}')

        self.stdout.write('Синхронизация завершена') 