from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = []

# Add render.com domain
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

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
    'blog.middleware.UserActivityMiddleware',
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
        }
    }
}

# Настройки для файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Создаем необходимые директории
REQUIRED_DIRS = [
    os.path.join(MEDIA_ROOT, 'avatars'),
    os.path.join(MEDIA_ROOT, 'posts'),
    os.path.join(MEDIA_ROOT, 'covers'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Настройки для постоянного хранения
PERSISTENT_DB = True
DB_PERSISTENT_STORAGE = True

# Настройки для бэкапов
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/opt/render/project/src/backups'}
DBBACKUP_CLEANUP_KEEP = 5
DBBACKUP_DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'

# Настройки для файлов
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Создаем необходимые директории
for directory in ['media', 'media/avatars', 'media/posts', 'media/covers', 'backups']:
    os.makedirs(os.path.join(BASE_DIR, directory), exist_ok=True)

# Настройки для бэкапов
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'backups')}
DBBACKUP_CLEANUP_KEEP = 5  # Хранить последние 5 бэкапов
DBBACKUP_DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'
DBBACKUP_FILENAME_TEMPLATE = '{datetime}.{extension}'

# Создаем необходимые директории
for directory in ['media', 'media/avatars', 'media/posts', 'media/covers', 'backups']:
    os.makedirs(os.path.join(BASE_DIR, directory), exist_ok=True)

# Настройки дл файлов
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Создаем необходимые директории
for directory in ['media/avatars', 'media/posts', 'media/covers']:
    os.makedirs(os.path.join(BASE_DIR, directory), exist_ok=True)

# Настройки для бэкапов
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'backups')}

# Добавляем логирование для отслеживания проблем с БД
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Отключаем сжатие и манифест для статических файлов
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Настройки для Whitenoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_MANIFEST_STRICT = False

# Настройки для статических файлов
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Создаем необходимые директории
REQUIRED_DIRS = [
    STATIC_ROOT,
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'static', 'css'),
    os.path.join(BASE_DIR, 'static', 'js'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Создаем необходимые директории
REQUIRED_DIRS = [
    STATIC_ROOT,
    MEDIA_ROOT,
    os.path.join(MEDIA_ROOT, 'avatars'),
    os.path.join(MEDIA_ROOT, 'posts'),
    os.path.join(MEDIA_ROOT, 'covers'),
    os.path.join(BASE_DIR, 'static', 'css'),
    os.path.join(BASE_DIR, 'static', 'js'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth settings
LOGIN_REDIRECT_URL = 'blog:home'
LOGOUT_REDIRECT_URL = 'blog:home'
LOGIN_URL = 'login'

# Admin settings
ADMIN_URL = 'admin/'

# Security settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# TinyMCE Configuration
TINYMCE_JS_URL = os.path.join(STATIC_URL, "tinymce/tinymce.min.js")
TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': 'auto',
    'menubar': False,
    'plugins': '''
        advlist autolink lists link image charmap print preview anchor
        searchreplace visualblocks code fullscreen
        insertdatetime media table paste code help wordcount
    ''',
    'toolbar': '''
        undo redo | formatselect | bold italic backcolor |
        alignleft aligncenter alignright alignjustify |
        bullist numlist outdent indent | removeformat | help |
        link image media | code fullscreen
    ''',
    'content_css': [
        '//fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
    ],
}

# Создаем необходимые директории
REQUIRED_DIRS = [
    STATIC_ROOT,
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'static', 'css'),
    os.path.join(BASE_DIR, 'static', 'js'),
    os.path.join(BASE_DIR, 'static', 'tinymce'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Настройки для статических файлов
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Добавляем MIME-типы
WHITENOISE_MIMETYPES = {
    '.js': 'application/javascript',
    '.css': 'text/css',
}

# Настройки для статических файов
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Настройки для медиа файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Добавляем настройки для аутентификации
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

# Настройки сессий
SESSION_COOKIE_AGE = 1209600  # 2 недели в секундах
SESSION_COOKIE_NAME = 'sessionid'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Добавляем бэкенды аутнтификации
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Для разработки
EMAIL_HOST = 'smtp.gmail.com'  # Дя продкшена
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')  # Ваш email
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # Пароль приложения
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# Добавьте/обновите эти настройки
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Создаем необходимые директории при запуске
REQUIRED_DIRS = [
    os.path.join(MEDIA_ROOT, 'avatars'),
    os.path.join(MEDIA_ROOT, 'covers'),
    os.path.join(MEDIA_ROOT, 'thumbnails'),
    os.path.join(MEDIA_ROOT, 'uploads'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Добавьте эти настройки для обработки файлов
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Настройки для медиа-файлов в продакшене
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
    
    # Создем необходимые директории
    REQUIRED_DIRS = [
        os.path.join(MEDIA_ROOT, 'avatars'),
        os.path.join(MEDIA_ROOT, 'covers'),
        os.path.join(MEDIA_ROOT, 'thumbnails'),
        os.path.join(MEDIA_ROOT, 'uploads'),
    ]

    for directory in REQUIRED_DIRS:
        os.makedirs(directory, exist_ok=True)

    # Устанавлиаем права доступа
    FILE_UPLOAD_PERMISSIONS = 0o644
    FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Настройки для Render.com
if os.environ.get('RENDER'):
    ALLOWED_HOSTS.append('.onrender.com')
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# В конце файла добавьте/обновите:
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Создаем необходимые директории
REQUIRED_DIRS = [
    os.path.join(MEDIA_ROOT, 'avatars'),
    os.path.join(MEDIA_ROOT, 'covers'),
    os.path.join(MEDIA_ROOT, 'thumbnails'),
    os.path.join(MEDIA_ROOT, 'uploads'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Убедитесь, что DEBUG = True для локальной разработки
DEBUG = True

# Настройка базы данных для Render.com
if os.environ.get('RENDER'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join('/opt/render/project/src/mysite', 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Настройки для постоянного хранения
PERSISTENT_DB = True
DB_PERSISTENT_STORAGE = True

# Настройки для файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = '/opt/render/project/src/media'  # Постоянная директория на Render
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Созаем директори для файлов
REQUIRED_DIRS = [
    os.path.join(MEDIA_ROOT, 'avatars'),
    os.path.join(MEDIA_ROOT, 'posts'),
    os.path.join(MEDIA_ROOT, 'covers'),
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Настройки для хранения файлов
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Настройки сессий для постоянного хранения
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

# Настройки для Render.com
if os.environ.get('RENDER'):
    ALLOWED_HOSTS.append('.onrender.com')
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)



