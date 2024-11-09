import os
import sys
from pathlib import Path

# Получаем абсолютный путь к директории проекта
BASE_DIR = Path(__file__).resolve().parent

# Добавляем пути в sys.path
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / 'config'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application() 