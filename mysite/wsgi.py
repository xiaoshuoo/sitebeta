import os
import sys

# Добавляем путь к проекту в PYTHONPATH для Render
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Получаем WSGI приложение
application = get_wsgi_application()