"""
WSGI config for config project.
"""

import os
import sys
from pathlib import Path

# Получаем абсолютный путь к директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Добавляем пути к проекту в sys.path
sys.path.append(str(BASE_DIR))
sys.path.append(os.path.join(BASE_DIR, 'config'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    print(f"Error loading application: {e}")
    print(f"sys.path: {sys.path}")
    raise
