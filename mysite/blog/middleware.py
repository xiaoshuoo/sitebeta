from django.utils import timezone

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Временно отключаем обновление last_seen
        response = self.get_response(request)
        return response