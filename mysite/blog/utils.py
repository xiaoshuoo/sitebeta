from contextlib import contextmanager
from django.db.models.signals import post_save

@contextmanager
def disable_signals():
    receivers = post_save.receivers
    post_save.receivers = []
    try:
        yield
    finally:
        post_save.receivers = receivers 