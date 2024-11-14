import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    # ... другие приложения ...
    'blog',
    # ... остальные приложения ...
]

# Добавьте настройки TinyMCE
TINYMCE_DEFAULT_CONFIG = {
    'height': 600,
    'width': 'auto',
    'menubar': 'file edit view insert format tools table help',
    'plugins': '''
        advlist autolink lists link image charmap print preview anchor
        searchreplace visualblocks code fullscreen emoticons
        insertdatetime media table paste code help wordcount codesample hr
        visualchars nonbreaking toc imagetools quickbars pagebreak
    ''',
    'toolbar': '''
        undo redo | formatselect | bold italic underline strikethrough | 
        forecolor backcolor | alignleft aligncenter alignright alignjustify | 
        bullist numlist outdent indent | removeformat | link image media table |
        codesample | fullscreen | emoticons hr | help
    ''',
    'content_css': [
        '//fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
        '//fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap',
    ],
    'content_style': '''
        body {
            font-family: Inter, sans-serif;
            background: #1a1625;
            color: #e2e8f0;
            padding: 20px;
            font-size: 16px;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #fff;
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.75em;
        }
        h1 { font-size: 2.25em; }
        h2 { font-size: 1.875em; }
        h3 { font-size: 1.5em; }
        h4 { font-size: 1.25em; }
        p { margin-bottom: 1em; }
        pre {
            background: #2d2a3d !important;
            color: #e2e8f0 !important;
            padding: 1rem;
            border-radius: 0.75rem;
            font-family: 'Fira Code', monospace;
            margin: 1.5em 0;
            overflow-x: auto;
        }
        code {
            background: #2d2a3d !important;
            color: #e2e8f0 !important;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-family: 'Fira Code', monospace;
        }
        blockquote {
            border-left: 4px solid #8b5cf6;
            margin: 1.5em 0;
            padding: 1em 1.5em;
            background: rgba(147, 51, 234, 0.1);
            border-radius: 0 0.5rem 0.5rem 0;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 0.5rem;
            margin: 1em 0;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1.5em 0;
            background: rgba(45, 42, 61, 0.5);
            border-radius: 0.5rem;
            overflow: hidden;
        }
        th, td {
            border: 1px solid rgba(147, 51, 234, 0.2);
            padding: 0.75rem;
            color: #e2e8f0;
        }
        th {
            background: rgba(147, 51, 234, 0.2);
            font-weight: 600;
        }
        tr:hover {
            background: rgba(147, 51, 234, 0.1);
        }
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(147, 51, 234, 0.5), transparent);
            margin: 2em 0;
        }
        a {
            color: #8b5cf6;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        a:hover {
            color: #a78bfa;
            text-decoration: underline;
        }
        ul, ol {
            padding-left: 1.5em;
            margin: 1em 0;
        }
        li {
            margin: 0.5em 0;
        }
    ''',
    'skin': 'oxide-dark',
    'content_css_dark': 'dark',
    'branding': False,
    'promotion': False,
    'statusbar': True,
    'elementpath': False,
    'resize': True,
    'paste_data_images': True,
    'image_advtab': True,
    'image_class_list': [
        {'title': 'Responsive', 'value': 'img-fluid rounded shadow-lg'},
    ],
    'style_formats': [
        {'title': 'Заголовки', 'items': [
            {'title': 'Заголовок 1', 'format': 'h1'},
            {'title': 'Заголовок 2', 'format': 'h2'},
            {'title': 'Заголовок 3', 'format': 'h3'},
            {'title': 'Заголовок 4', 'format': 'h4'},
        ]},
        {'title': 'Блоки', 'items': [
            {'title': 'Параграф', 'format': 'p'},
            {'title': 'Блок кода', 'format': 'pre'},
            {'title': 'Цитата', 'format': 'blockquote'},
        ]},
        {'title': 'Встроенные', 'items': [
            {'title': 'Жирный', 'format': 'bold'},
            {'title': 'Курсив', 'format': 'italic'},
            {'title': 'Подчеркнутый', 'format': 'underline'},
            {'title': 'Зачеркнутый', 'format': 'strikethrough'},
            {'title': 'Код', 'format': 'code'},
        ]},
    ],
    'quickbars_selection_toolbar': 'bold italic underline strikethrough | formatselect | blockquote quicklink',
    'quickbars_insert_toolbar': 'image media table hr codesample',
    'contextmenu': 'link image imagetools table spellchecker',
    'custom_colors': False,
    'color_map': [
        '8B5CF6', 'Primary',
        '7C3AED', 'Primary Dark',
        'E2E8F0', 'Text',
        '94A3B8', 'Text Light',
        '1A1625', 'Background',
        '2D2A3D', 'Surface',
    ],
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