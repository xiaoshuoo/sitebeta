"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Получаем абсолютный путь к директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Выводим отладочную информацию
print(f"BASE_DIR: {BASE_DIR}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")
print(f"Files in config directory: {os.listdir('config')}")
print(f"Python path before: {sys.path}")

# Добавляем путь к проекту в sys.path
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

print(f"Python path after: {sys.path}")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    print(f"Error loading application: {e}")
    raise
