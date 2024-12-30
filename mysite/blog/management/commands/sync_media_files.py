from django.core.management.base import BaseCommand
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = 'Синхронизация медиа файлов'

    def handle(self, *args, **options):
        # Создаем директории если их нет
        media_dirs = [
            'avatars',
            'posts',
            'thumbnails',
            'covers'
        ]
        
        # Создаем локальные директории
        for directory in media_dirs:
            local_path = os.path.join(settings.BASE_DIR, 'media', directory)
            os.makedirs(local_path, exist_ok=True)
            
            # Создаем серверные директории если не в режиме отладки
            if not settings.DEBUG:
                server_path = os.path.join(settings.MEDIA_ROOT, directory)
                os.makedirs(server_path, exist_ok=True)
                os.chmod(server_path, 0o777)

        self.stdout.write(self.style.SUCCESS('Директории успешно созданы')) 