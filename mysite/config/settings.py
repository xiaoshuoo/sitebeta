from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-default-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

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
    'tinymce',
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
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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
    'content_style': '''
        body {
            font-family: Inter, sans-serif;
            font-size: 16px;
            color: white;
            background-color: #1a1625;
            padding: 20px;
            max-width: 100%;
            margin: 0;
        }
        p { line-height: 1.6; margin-bottom: 1em; color: #e2e8f0; }
        h1, h2, h3, h4, h5, h6 { color: white; }
    ''',
    'skin': 'oxide-dark',
    'content_css_dark': 'dark',
}

# TinyMCE API Key
TINYMCE_API_KEY = '69ivue7aox9alaq0v8pv90xk8iysctulgxmx7px3ler2pnp4'

# Создаем директории если их нет
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')
os.makedirs(CKEDITOR_UPLOAD_PATH, exist_ok=True)

# Настройка для статических файлов
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Добавляем MIME-типы
WHITENOISE_MIMETYPES = {
    '.js': 'application/javascript',
    '.css': 'text/css',
}

# Настройки для статических файлов
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

# Добавляем бэкенды аутентификации
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Для разработки
EMAIL_HOST = 'smtp.gmail.com'  # Для продакшена
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')  # Ваш email
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # Пароль приложения
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')



