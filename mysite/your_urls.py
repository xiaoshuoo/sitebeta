from django.contrib.auth.views import LogoutView

urlpatterns = [
    # ...
    path('accounts/logout/', LogoutView.as_view(http_method_names=['get', 'post']), name='logout'),
    # ...
] 