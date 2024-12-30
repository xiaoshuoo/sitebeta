from cloudinary_storage.storage import MediaCloudinaryStorage
import cloudinary.uploader
import logging
import os
from django.conf import settings
import uuid

logger = logging.getLogger(__name__)

class CustomCloudinaryStorage(MediaCloudinaryStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_backup_dir = os.path.join(settings.BASE_DIR, 'media_backup')
        os.makedirs(self.local_backup_dir, exist_ok=True)

    def _get_resource_type(self, name):
        """Определяет тип ресурса"""
        ext = os.path.splitext(name)[1].lower()
        if ext in ['.gif', '.jpg', '.jpeg', '.png', '.webp']:
            return 'image'
        elif ext in ['.mp4', '.webm', '.mov']:
            return 'video'
        return 'raw'

    def _save(self, name, content):
        """Сохраняет файл в Cloudinary"""
        try:
            # Генерируем уникальное имя файла
            ext = os.path.splitext(name)[1].lower()
            filename = f"{uuid.uuid4()}{ext}"
            
            # Определяем папку на основе пути
            if 'avatars' in name:
                folder = 'avatars'
            elif 'covers' in name:
                folder = 'covers'
            elif 'thumbnails' in name:
                folder = 'thumbnails'
            else:
                folder = 'posts'

            # Загружаем в Cloudinary
            result = cloudinary.uploader.upload(
                content,
                folder=folder,  # Используем folder вместо включения в public_id
                public_id=os.path.splitext(filename)[0],  # Только имя файла без расширения
                resource_type=self._get_resource_type(name),
                unique_filename=True,
                overwrite=True
            )
            logger.info(f"Successfully uploaded to Cloudinary: {folder}/{filename}")

            # Создаем локальную резервную копию
            backup_path = os.path.join(self.local_backup_dir, folder, filename)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            with open(backup_path, 'wb') as f:
                content.seek(0)
                f.write(content.read())
            logger.info(f"Created local backup: {backup_path}")

            return result['secure_url']
        except Exception as e:
            logger.error(f"Error uploading to Cloudinary: {str(e)}")
            raise

    def url(self, name):
        """Получаем URL файла"""
        try:
            # Определяем папку
            if 'avatars' in name:
                folder = 'avatars'
            elif 'covers' in name:
                folder = 'covers'
            elif 'thumbnails' in name:
                folder = 'thumbnails'
            else:
                folder = 'posts'

            # Получаем только имя файла
            filename = os.path.basename(name)
            public_id = f"{folder}/{os.path.splitext(filename)[0]}"

            return cloudinary.CloudinaryImage(public_id).build_url(secure=True)
        except Exception as e:
            logger.error(f"Error getting URL: {str(e)}")
            return None

    def exists(self, name):
        """Проверяем существование файла"""
        try:
            folder = 'posts'
            if 'avatars' in name:
                folder = 'avatars'
            elif 'covers' in name:
                folder = 'covers'
            elif 'thumbnails' in name:
                folder = 'thumbnails'

            filename = os.path.basename(name)
            public_id = f"{folder}/{os.path.splitext(filename)[0]}"
            
            result = cloudinary.api.resource(public_id)
            return True
        except:
            backup_path = os.path.join(self.local_backup_dir, folder, filename)
            return os.path.exists(backup_path)

    def delete(self, name):
        """Удаляем файл"""
        try:
            folder = 'posts'
            if 'avatars' in name:
                folder = 'avatars'
            elif 'covers' in name:
                folder = 'covers'
            elif 'thumbnails' in name:
                folder = 'thumbnails'

            filename = os.path.basename(name)
            public_id = f"{folder}/{os.path.splitext(filename)[0]}"
            
            cloudinary.uploader.destroy(public_id)
            logger.info(f"File deleted from Cloudinary: {public_id}")

            backup_path = os.path.join(self.local_backup_dir, folder, filename)
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logger.info(f"Deleted local backup: {backup_path}")
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")