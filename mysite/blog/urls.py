from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница блога
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('categories/', views.categories, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('invites/', views.invite_codes, name='invite_codes'),
    path('invites/create/', views.create_invite, name='create_invite'),
    path('register/', views.register, name='register'),
] 