from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Настройки для Whitenoise
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_AUTOREFRESH = True

# Настройки для медиа файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Создаем необходимые директории
REQUIRED_DIRS = [
    STATIC_ROOT,
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'static', 'css'),
    os.path.join(BASE_DIR, 'static', 'js'),
    MEDIA_ROOT,
    os.path.join(MEDIA_ROOT, 'avatars'),
    os.path.join(MEDIA_ROOT, 'posts'),
    os.path.join(MEDIA_ROOT, 'covers'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Включаем режим отладки для локальной разработки

# Настройки хостов
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

# Отключаем все настройки SSL и HTTPS для локальной разработки
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
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
    'blog.middleware.DatabaseConnectionMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://django_blog_7f9a_user:qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE@dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com/django_blog_7f9a')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_blog_7f9a',
        'USER': 'django_blog_7f9a_user',
        'PASSWORD': 'qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
        'HOST': 'dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
            'keepalives': 1,
            'keepalives_idle': 130,
            'keepalives_interval': 10,
            'keepalives_count': 10,
            'client_encoding': 'UTF8',
        },
        'CONN_MAX_AGE': None,  # Постоянное соединение
        'ATOMIC_REQUESTS': True,  # Транзакции для каждого запроса
        'CONN_HEALTH_CHECKS': True,
    }
}

# Настройки для файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Настройки для сессий
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 недели
SESSION_SAVE_EVERY_REQUEST = True

# Настройки кэширования
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
        'TIMEOUT': None,
        'OPTIONS': {
            'MAX_ENTRIES': 100000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Настройки для постоянного хранения
PERSISTENT_DB = True
DB_PERSISTENT_STORAGE = True

# Настройки для бэкапов
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'backups')}
DBBACKUP_CLEANUP_KEEP = 5
DBBACKUP_DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'

# Добавляем логирование для отслеживания проблем с БД
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'db.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Создаем необходимые директории
REQUIRED_DIRS = [
    os.path.join(MEDIA_ROOT, 'avatars'),
    os.path.join(MEDIA_ROOT, 'posts'),
    os.path.join(MEDIA_ROOT, 'covers'),
    os.path.join(BASE_DIR, 'backups'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Настройки для файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Создаем необходимые директории
for directory in ['media/avatars', 'media/posts', 'media/covers', 'static/css', 'static/js']:
    os.makedirs(os.path.join(BASE_DIR, directory), exist_ok=True)

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://sity-lvo8.onrender.com',
    'https://*.render.com',
]

# Настройки безопасности
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Отключаем HSTS
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Настройки для работы с HTTP
USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False

# Настройки для Whitenoise
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_AUTOREFRESH = True

# Настройки для медиа файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Создаем необходимые директории
REQUIRED_DIRS = [
    STATIC_ROOT,
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'static', 'css'),
    os.path.join(BASE_DIR, 'static', 'js'),
    MEDIA_ROOT,
    os.path.join(MEDIA_ROOT, 'avatars'),
    os.path.join(MEDIA_ROOT, 'posts'),
    os.path.join(MEDIA_ROOT, 'covers'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)



