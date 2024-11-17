from django.utils import timezone
from django.db import connection
from django.db.utils import OperationalError

class DatabaseConnectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем подключение к БД перед каждым запросом
        try:
            connection.ensure_connection()
            if not connection.is_usable():
                connection.connect()
        except OperationalError:
            # Пробуем переподключиться
            connection.connect()

        response = self.get_response(request)

        # Обновляем last_seen для авторизованных пользователей
        if request.user.is_authenticated:
            try:
                request.user.profile.last_seen = timezone.now()
                request.user.profile.save(update_fields=['last_seen'])
            except:
                pass

        return response

    def process_exception(self, request, exception):
        if isinstance(exception, OperationalError):
            # Если произошла ошибка базы данных, пробуем переподключиться
            try:
                connection.connect()
            except:
                pass
        return None