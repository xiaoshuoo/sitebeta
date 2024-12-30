from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Profile, Post
import os
import shutil

class Command(BaseCommand):
    help = 'Проверяет и восстанавливает медиа файлы'

    def handle(self, *args, **options):
        # Проверяем существование директорий
        for directory in settings.MEDIA_DIRS:
            path = os.path.join(settings.MEDIA_ROOT, directory)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                if not settings.DEBUG:
                    os.chmod(path, 0o777)
                self.stdout.write(f'Created directory: {path}')

        # Проверяем файлы аватаров
        for profile in Profile.objects.all():
            if profile.avatar and not os.path.exists(profile.avatar.path):
                self.stdout.write(f'Missing avatar for user: {profile.user.username}')
                # Здесь можно добавить логику восстановления из бэкапа

        # Проверяем файлы постов
        for post in Post.objects.all():
            if post.thumbnail and not os.path.exists(post.thumbnail.path):
                self.stdout.write(f'Missing thumbnail for post: {post.title}')
                # Здесь можно добавить логику восстановления из бэкапа 