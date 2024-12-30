import os
from django.conf import settings
import logging
import shutil

logger = logging.getLogger(__name__)

class StorageSync:
    def __init__(self):
        self.local_media_root = settings.MEDIA_ROOT
        self.local_backup_root = settings.MEDIA_BACKUP_ROOT
        
        # Создаем локальные директории если их нет
        os.makedirs(self.local_media_root, exist_ok=True)
        os.makedirs(self.local_backup_root, exist_ok=True)

    def backup_file(self, file_path):
        """Создает резервную копию файла"""
        try:
            if os.path.exists(file_path):
                relative_path = os.path.relpath(file_path, self.local_media_root)
                backup_path = os.path.join(self.local_backup_root, relative_path)
                
                # Создаем директорию для бэкапа если её нет
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                
                # Копируем файл
                shutil.copy2(file_path, backup_path)
                logger.info(f"Created backup: {relative_path}")
                return True
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
        return False

    def restore_file(self, file_path):
        """Восстанавливает файл из резервной копии"""
        try:
            relative_path = os.path.relpath(file_path, self.local_media_root)
            backup_path = os.path.join(self.local_backup_root, relative_path)
            
            if os.path.exists(backup_path):
                # Создаем директорию если её нет
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Восстанавливаем файл
                shutil.copy2(backup_path, file_path)
                logger.info(f"Restored file: {relative_path}")
                return True
        except Exception as e:
            logger.error(f"Restore error: {str(e)}")
        return False

    def sync_all(self):
        """Синхронизирует все файлы"""
        try:
            # Восстанавливаем файлы из бэкапа
            for root, dirs, files in os.walk(self.local_backup_root):
                for file in files:
                    backup_path = os.path.join(root, file)
                    relative_path = os.path.relpath(backup_path, self.local_backup_root)
                    media_path = os.path.join(self.local_media_root, relative_path)
                    
                    if not os.path.exists(media_path):
                        self.restore_file(media_path)
            
            # Создаем бэкапы новых файлов
            for root, dirs, files in os.walk(self.local_media_root):
                for file in files:
                    media_path = os.path.join(root, file)
                    relative_path = os.path.relpath(media_path, self.local_media_root)
                    backup_path = os.path.join(self.local_backup_root, relative_path)
                    
                    if not os.path.exists(backup_path):
                        self.backup_file(media_path)
                        
            return True
        except Exception as e:
            logger.error(f"Sync error: {str(e)}")
            return False 