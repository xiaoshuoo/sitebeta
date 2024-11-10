from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),  # Корневой URL
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.post_delete, name='delete_post'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('categories/', views.categories_list, name='categories'),
    path('category/<str:slug>/', views.category_detail, name='category_detail'),
    path('tag/<str:slug>/', views.tag_detail, name='tag_detail'),
    path('invite/create/', views.create_invite, name='create_invite'),
    path('invite/list/', views.invite_codes, name='invite_codes'),
    path('about/', views.about, name='about'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('panel/', views.admin_panel, name='admin_panel'),
    path('panel/clear-cache/', views.clear_cache, name='clear_cache'),
    path('panel/toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
] 