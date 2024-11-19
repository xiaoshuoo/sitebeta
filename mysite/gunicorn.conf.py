import multiprocessing
import os
import sys

# Получаем абсолютный путь к директории проекта
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

# Добавляем путь к директории mysite
mysite_path = os.path.join(project_path, 'mysite')
sys.path.append(mysite_path)

# Настройки Gunicorn
bind = "0.0.0.0:10000"  # Порт будет автоматически установлен Render
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "config.wsgi:application"