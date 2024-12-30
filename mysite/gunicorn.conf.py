import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 300
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'gunicorn_django'
django_settings = 'config.settings'

# SSL
keyfile = None
certfile = None

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Debug
reload = False
reload_engine = 'auto'
spew = False

# Server hooks
def on_starting(server):
    server.log.info("Server is starting")

def on_reload(server):
    server.log.info("Server is reloading")

def when_ready(server):
    server.log.info("Server is ready")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")