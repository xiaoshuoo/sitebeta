from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', RedirectView.as_view(url='/blog/', permanent=True)),
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='blog:home',
        template_name='registration/logged_out.html'
    ), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        path('static/<path:path>', RedirectView.as_view(url=settings.STATIC_URL + '%(path)s')),
        path('media/<path:path>', RedirectView.as_view(url=settings.MEDIA_URL + '%(path)s')),
    ]