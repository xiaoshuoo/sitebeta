"""
WSGI конфигурация для проекта.
"""
import os
import sys
from pathlib import Path

# Получаем корневую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Добавляем пути проекта в Python path
paths = [
    str(BASE_DIR),
    str(BASE_DIR / 'config'),
]

for path in paths:
    if path not in sys.path:
        sys.path.insert(0, path)

# Выводим отладочную информацию
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print("Project directory:", BASE_DIR)
print("Directory contents:", os.listdir(BASE_DIR))
print("Config directory contents:", os.listdir(BASE_DIR / 'config'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    print(f"Error loading application: {e}")
    raise
