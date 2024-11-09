# Gunicorn configuration file
import multiprocessing

max_requests = 1000
max_requests_jitter = 50

log_file = "-"
log_level = "debug"

bind = "0.0.0.0:$PORT"
workers = multiprocessing.cpu_count() * 2 + 1

timeout = 120
keepalive = 5

capture_output = True
enable_stdio_inheritance = True

preload_app = True