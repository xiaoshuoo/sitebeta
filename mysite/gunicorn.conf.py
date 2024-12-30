import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes - устанавливаем фиксированное количество
workers = 4
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

def when_ready(server):
    server.log.info("Server is ready. Starting to accept requests...")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")

def pre_fork(server, worker):
    server.log.info(f"Pre-fork: Preparing worker {worker.age}")

def post_fork(server, worker):
    server.log.info(f"Post-fork: Worker {worker.pid} spawned successfully")

def pre_exec(server):
    server.log.info("Pre-exec: Forked child, re-executing.")

def worker_exit(server, worker):
    server.log.info(f"Worker {worker.pid} exited")