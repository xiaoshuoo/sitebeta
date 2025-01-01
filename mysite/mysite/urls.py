from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import backup_database
import atexit

# Регистрируем функцию бэкапа при выключении
atexit.register(backup_database)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),  # Включаем URL-шаблоны блога
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 