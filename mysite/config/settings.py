from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'blog.apps.BlogConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'blog.middleware.UserActivityMiddleware',
    'blog.middleware.SessionRefreshMiddleware',
    'blog.middleware.StorageSyncMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates', 'registration'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'b3fbgpfjiisirtqyqdry',
        'USER': 'utihi7xqxpcfj2b5nzxr',
        'PASSWORD': 'JMq9iLTaBX23jV4oFu9JsIqHIO45dB',
        'HOST': 'b3fbgpfjiisirtqyqdry-postgresql.services.clever-cloud.com',
        'PORT': '50013',
        'OPTIONS': {
            'sslmode': 'disable',  # Отключаем SSL для тестирования
            'connect_timeout': 30,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'client_encoding': 'UTF8',
        },
        'CONN_MAX_AGE': 0,
        'ATOMIC_REQUESTS': True,
        'AUTOCOMMIT': True,
    }
}

# Настройки для отладки проблем с БД
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'debug.log',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'blog': {  # Для вашего приложения
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'django': {  # Для Django
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

# Настройки кэширования
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Настройки сессий
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 30  # 30 дней
SESSION_SAVE_EVERY_REQUEST = True

# Настройки безопасности для PostgreSQL
CONN_MAX_AGE = 60  # Время жизни соединения в секундах
ATOMIC_REQUESTS = True  # Автоматические транзакции для каждого запроса

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Базовые пути для хранения файлов
BASE_MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
BASE_STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Определяем пути для хранения файлов
if DEBUG:
    # Локальные пути
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = BASE_MEDIA_ROOT
else:
    # Пути на сервере Render
    STATIC_ROOT = '/opt/render/project/src/staticfiles'
    MEDIA_ROOT = '/opt/render/project/src/media'

# Настройки для загрузки файлов
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Настройки для обработки загрузки файлов
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Настройки для медиа директоий
MEDIA_DIRS = {
    'avatars': {
        'path': 'avatars',
        'allowed_types': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'max_size': 20 * 1024 * 1024  # 20MB
    },
    'posts': {
        'path': 'posts',
        'allowed_types': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'max_size': 50 * 1024 * 1024  # 50MB
    },
    'thumbnails': {
        'path': 'thumbnails',
        'allowed_types': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'max_size': 30 * 1024 * 1024  # 30MB
    }
}

# Настройки для хранения файлов
DEFAULT_FILE_STORAGE = 'blog.cloudinary_storage.CustomCloudinaryStorage'
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Добавляем настройки для сжатия изображений
IMAGE_COMPRESSION = {
    'enabled': False,  # Отключаем сжатие для GIF
    'quality': 90,     # Качество для JPEG
    'optimize': True   # Оптимизация PNG
}

# Настройки для синхронизации файлов
SYNC_MEDIA = True
SYNC_ON_SAVE = True  # Синхронизировать при сохранении файлов
SYNC_DELETE = True   # Синхронизировать удаление файлов

# Общие директории для статических айлов
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Добавьте настройки для CKEditor
CKEDITOR_BASEPATH = "/static/js/ckeditor/"
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

# Создаем директории если их нет
for dir_config in MEDIA_DIRS.values():
    dir_path = dir_config['path']
    local_path = os.path.join(MEDIA_ROOT, dir_path)
    os.makedirs(local_path, exist_ok=True)
    if not DEBUG:
        os.chmod(local_path, 0o777)

# Настройки сессий
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 30  # 30 дней
SESSION_SAVE_EVERY_REQUEST = True

# В конец файла добавьте:
DEFAULT_FILE_STORAGE = 'blog.cloudinary_storage.CustomCloudinaryStorage'

# Настройки для медиа-файлов
MEDIA_BACKUP_ROOT = os.path.join(BASE_DIR, 'media_backup')
os.makedirs(MEDIA_BACKUP_ROOT, exist_ok=True)

# Создаем директории для бэкапов
for dir_name in ['avatars', 'posts', 'thumbnails', 'covers']:
    backup_dir = os.path.join(MEDIA_BACKUP_ROOT, dir_name)
    os.makedirs(backup_dir, exist_ok=True)

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'media.log'),
        },
    },
    'loggers': {
        'blog.storage': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Настройки для медиа-файлов
MEDIA_BACKUP_ENABLED = True
MEDIA_BACKUP_ROOT = os.path.join(BASE_DIR, 'media_backup')
MEDIA_SYNC_INTERVAL = 300  # 5 минут

# Создаем необходимые директории
for dir_name in ['avatars', 'posts', 'thumbnails', 'covers']:
    os.makedirs(os.path.join(MEDIA_ROOT, dir_name), exist_ok=True)
    os.makedirs(os.path.join(MEDIA_BACKUP_ROOT, dir_name), exist_ok=True)

# Cloudinary settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dztabzn19',
    'API_KEY': '637516781124235',
    'API_SECRET': 'IlGJ1ZByBxMee-p-BwUWcN7498c',
    'SECURE': True,
}

# Configure Cloudinary
cloudinary.config( 
    cloud_name = CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key = CLOUDINARY_STORAGE['API_KEY'],
    api_secret = CLOUDINARY_STORAGE['API_SECRET'],
    secure = CLOUDINARY_STORAGE['SECURE']
)

# Storage settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Static files settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Whitenoise settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Whitenoise options
WHITENOISE_MIMETYPES = {
    '.svg': 'image/svg+xml',
    '.woff': 'application/font-woff',
    '.woff2': 'application/font-woff2',
}

WHITENOISE_ALLOW_ALL_ORIGINS = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = [
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2',
    'rar', 'svg', 'woff', 'woff2'
]

# Authentication settings
LOGIN_REDIRECT_URL = '/'  # Redirect to home page after login
LOGOUT_REDIRECT_URL = '/'  # Redirect to home page after logout


