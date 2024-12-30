from cloudinary_storage.storage import MediaCloudinaryStorage
import cloudinary.uploader
import logging
import os
from django.core.files.base import File
from django.core.files.uploadedfile import UploadedFile
import io
import time

logger = logging.getLogger(__name__)

class CustomCloudinaryStorage(MediaCloudinaryStorage):
    def _save(self, name, content):
        try:
            # Очищаем имя файла
            clean_name = name.replace('\\', '/').lstrip('/')
            
            # Загружаем файл в Cloudinary с полным путем
            result = cloudinary.uploader.upload(
                content,
                public_id=clean_name,
                resource_type="auto",
                overwrite=True,
                invalidate=True
            )
            
            logger.info(f"Successfully uploaded to Cloudinary: {clean_name}")
            return clean_name
            
        except Exception as e:
            logger.error(f"Error uploading to Cloudinary: {str(e)}")
            raise e

    def _open(self, name, mode='rb'):
        url = self.url(name)
        if url:
            return File(io.BytesIO(), name=name)
        return None

    def url(self, name):
        try:
            if not name:
                return None
            
            # Очищаем имя файла от лишних слешей
            clean_name = name.replace('\\', '/').lstrip('/')
            
            # Используем полный путь как public_id
            image = cloudinary.CloudinaryImage(clean_name)
            
            # Базовые параметры
            options = {
                'secure': True,
                'format': 'auto',
                'quality': 'auto'
            }
            
            # Специфичные настройки для разных типов файлов
            if 'avatars/' in clean_name:
                options.update({
                    'width': 400,
                    'height': 400,
                    'crop': 'fill',
                    'gravity': 'face'
                })
            elif 'covers/' in clean_name:
                options.update({
                    'width': 1500,
                    'height': 500,
                    'crop': 'fill',
                    'gravity': 'center'
                })
            
            # Получаем URL
            url = image.build_url(**options)
            logger.info(f"Generated URL for {clean_name}: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error getting URL from Cloudinary: {str(e)}")
            return None

    def exists(self, name):
        try:
            if not name:
                return False
                
            # Convert Windows path separators
            clean_name = name.replace('\\', '/')
            
            # Проверяем существование файла
            result = cloudinary.api.resource(clean_name)
            return True
        except:
            return False

    def delete(self, name):
        try:
            if not name:
                return
                
            # Convert Windows path separators
            clean_name = name.replace('\\', '/')
            
            # Удаляем файл
            cloudinary.uploader.destroy(clean_name)
            logger.info(f"File deleted from Cloudinary: {clean_name}")
        except Exception as e:
            logger.error(f"Error deleting from Cloudinary: {str(e)}") 