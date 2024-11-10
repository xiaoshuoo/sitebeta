import os
from django.core.wsgi import get_wsgi_application

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Получаем WSGI приложение
application = get_wsgi_application() 