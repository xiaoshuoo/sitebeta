from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Проверяет и восстанавливает медиа-файлы из резервных копий'

    def handle(self, *args, **options):
        backup_dir = os.path.join(settings.BASE_DIR, 'media_backup')
        media_root = settings.MEDIA_ROOT

        # Проверяем каждую директорию
        for dir_name in ['avatars', 'posts', 'thumbnails', 'covers']:
            backup_path = os.path.join(backup_dir, dir_name)
            media_path = os.path.join(media_root, dir_name)
            
            # Создаем директории если их нет
            os.makedirs(backup_path, exist_ok=True)
            os.makedirs(media_path, exist_ok=True)

            # Восстанавливаем файлы
            for filename in os.listdir(backup_path):
                backup_file = os.path.join(backup_path, filename)
                media_file = os.path.join(media_path, filename)
                
                if not os.path.exists(media_file):
                    try:
                        shutil.copy2(backup_file, media_file)
                        self.stdout.write(
                            self.style.SUCCESS(f'Restored: {filename}')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error restoring {filename}: {e}')
                        ) 