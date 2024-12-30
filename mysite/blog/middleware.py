from django.utils import timezone
from django.contrib.sessions.models import Session
from .storage_sync import StorageSync
import time

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Временно отключаем обновление last_seen
        response = self.get_response(request)
        return response

class SessionRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Обновляем время последней активности
        if request.user.is_authenticated:
            request.user.profile.last_seen = timezone.now()
            request.user.profile.save()

        # Обновляем сессию
        # Проверяем, является ли запрос AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if not is_ajax:
            request.session.modified = True

        response = self.get_response(request)
        return response

class StorageSyncMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_sync = 0
        self.sync_interval = 300  # 5 минут

    def __call__(self, request):
        # Проверяем нужно ли синхронизировать
        current_time = time.time()
        if current_time - self.last_sync > self.sync_interval:
            storage_sync = StorageSync()
            storage_sync.sync_all()
            self.last_sync = current_time

        response = self.get_response(request)
        return response