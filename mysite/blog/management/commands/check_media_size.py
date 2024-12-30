from django.core.management.base import BaseCommand
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Проверка размера медиа-файлов'

    def get_size_format(self, size):
        """Конвертация размера в читаемый формат"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def get_dir_size(self, path):
        """Получение размера директории"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        
        # Проверяем общий размер медиа-директории
        total_size = self.get_dir_size(media_root)
        self.stdout.write(f"Общий размер медиа-файлов: {self.get_size_format(total_size)}")
        
        # Проверяем размер по категориям
        for dir_name in ['avatars', 'posts', 'thumbnails', 'covers']:
            dir_path = os.path.join(media_root, dir_name)
            if os.path.exists(dir_path):
                size = self.get_dir_size(dir_path)
                self.stdout.write(f"Размер {dir_name}: {self.get_size_format(size)}")
                
                # Показываем список файлов
                self.stdout.write(f"\nФайлы в {dir_name}:")
                for file_name in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, file_name)
                    file_size = os.path.getsize(file_path)
                    self.stdout.write(f"  - {file_name}: {self.get_size_format(file_size)}") 