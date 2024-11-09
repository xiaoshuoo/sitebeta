import os
import sys
from pathlib import Path

# Получаем абсолютный путь к директории проекта
BASE_DIR = Path(__file__).resolve().parent

# Выводим отладочную информацию
print(f"Current directory: {os.getcwd()}")
print(f"BASE_DIR: {BASE_DIR}")
print(f"Directory contents: {os.listdir('.')}")
print(f"Python path before: {sys.path}")

# Добавляем пути в sys.path
sys.path.insert(0, str(BASE_DIR))

# Проверяем наличие файлов
config_init = BASE_DIR / 'config' / '__init__.py'
config_settings = BASE_DIR / 'config' / 'settings.py'
print(f"config/__init__.py exists: {config_init.exists()}")
print(f"config/settings.py exists: {config_settings.exists()}")
print(f"Python path after: {sys.path}")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    print(f"Error loading application: {e}")
    print(f"Current directory contents: {os.listdir('.')}")
    print(f"Config directory contents: {os.listdir('config')}")
    raise 