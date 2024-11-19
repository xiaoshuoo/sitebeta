import multiprocessing
import os
import sys

# Добавляем путь к проекту в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройки Gunicorn
bind = "0.0.0.0:10000"  # Порт будет автоматически установлен Render
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "config.wsgi:application"  # Убрали mysite из пути