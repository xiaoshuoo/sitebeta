from pathlib import Path
import os
import dj_database_url

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
        ssl_require=False
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
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

# TinyMCE settings
TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
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
        link image media | code
    ''',
    'content_css': 'dark',
}

TINYMCE_JS_URL = 'https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js'
TINYMCE_COMPRESSOR = False

# Message settings
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Proxy settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# File upload permissions
FILE_UPLOAD_PERMISSIONS = 0o644

# Создаем директории для загрузок
CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads/')
os.makedirs(CKEDITOR_UPLOAD_PATH, exist_ok=True)

# CKEditor settings
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-dark',
        'toolbar': 'Custom',
        'height': 500,
        'width': 'auto',
        'toolbar_Custom': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'],
            ['Link', 'Unlink'],
            ['Image', 'Table'],
            ['Source'],
            ['Maximize']
        ],
        'extraPlugins': ','.join([
            'uploadimage',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
        'removePlugins': ','.join(['image']),
        'allowedContent': True,
        'removeFormatAttributes': '',
        'enterMode': 2,
        'height': '500px',
        'contentsCss': [
            '/static/ckeditor/ckeditor/contents.css',
            '/static/css/custom-ckeditor.css'
        ],
    }
}

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False

# Создаем директории для загрузок
import os
CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads/')
os.makedirs(CKEDITOR_UPLOAD_PATH, exist_ok=True)