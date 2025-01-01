import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
    'tinymce',
    'whitenoise.runserver_nostatic',
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
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Добавьте настройки TinyMCE
TINYMCE_DEFAULT_CONFIG = {
    'height': 600,
    'width': 'auto',
    'menubar': 'file edit view insert format tools table help',
    'plugins': '''
        advlist autolink lists link image charmap preview anchor
        searchreplace visualblocks code fullscreen emoticons codesample
        insertdatetime media table paste code help wordcount
    ''',
    'toolbar': '''
        undo redo | blocks | bold italic backcolor | 
        alignleft aligncenter alignright alignjustify |
        bullist numlist outdent indent | link image media | codesample |
        removeformat | help | emoticons | fullscreen
    ''',
    'skin': 'oxide-dark',
    'content_css': 'dark',
    'branding': False,
    'promotion': False,
    'content_style': '''
        body {
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: #e2e8f0;
            background-color: #1a1625;
            padding: 20px;
            max-width: 100%;
        }
        p { margin: 1em 0; }
        h1, h2, h3, h4, h5, h6 { color: #fff; }
        a { color: #8B5CF6; }
        img { max-width: 100%; height: auto; border-radius: 8px; }
        pre { background: rgba(0, 0, 0, 0.2); padding: 15px; border-radius: 8px; }
        blockquote { 
            border-left: 4px solid #8B5CF6;
            margin: 1.5em 0;
            padding: 1em 1.5em;
            background: rgba(139, 92, 246, 0.1);
        }
    '''
}

# Настройки для бэкапов
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# Создаем директорию для бэкапов, если она не существует
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# Настройки для SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'BACKUP_ENABLED': True,  # Включаем бэкапы
        'BACKUP_DIRECTORY': BACKUP_DIR,  # Директория для бэкапов
    }
}

# Настройки медиа-файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 