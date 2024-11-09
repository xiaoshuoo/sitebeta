import os
import sys
from pathlib import Path

# Получаем абсолютный путь к директории проекта
BASE_DIR = Path(__file__).resolve().parent

# Выводим отладочную информацию
print(f"Current directory: {os.getcwd()}")
print(f"BASE_DIR: {BASE_DIR}")
print(f"Directory contents: {os.listdir('.')}")

# Добавляем пути в sys.path
sys.path.insert(0, str(BASE_DIR))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application() 