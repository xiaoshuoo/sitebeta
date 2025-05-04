from django.urls import path
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from .views import ProfileUpdateView, search
from django.conf import settings
from django.conf.urls.static import static

app_name = 'blog'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('categories/', views.categories_list, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/cover/', views.update_profile_cover, name='update_profile_cover'),
    path('profile/avatar/', views.update_profile_avatar, name='update_profile_avatar'),
    path('profile/cover/remove/', views.remove_profile_cover, name='remove_profile_cover'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('search/', views.search, name='search'),
    path('lecture/', views.lecture_page, name='lecture_page'),
    path('posts/', views.post_list, name='post_list'),
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url='/password_change/done/'
         ), 
         name='password_change'
    ),
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html'
         ), 
         name='password_change_done'
    ),
    path('update-activity/', views.update_activity, name='update_activity'),
    path('set-offline/', views.set_offline, name='set_offline'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='blog:home'), name='logout'),
    path('health/', views.health_check, name='health'),
    path('panel/', views.admin_panel, name='admin_panel'),
    path('panel/clear-cache/', views.clear_cache, name='clear_cache'),
    path('panel/toggle-page/<str:page_name>/', views.toggle_page_status, name='toggle_page_status'),
    path('panel/backup/', views.generate_backup, name='backup_database'),
    path('panel/clean-database/', views.clean_database, name='clean_database'),
    path('panel/restore-media/', views.restore_media, name='restore_media'),
    path('panel/create-invite/', views.create_invite, name='create_invite'),
    path('panel/deactivate-invite/<str:code>/', views.deactivate_invite, name='deactivate_invite'),
    path('panel/users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('panel/text-templates/', views.text_templates, name='text_templates'),
    path('panel/text-templates/<int:template_id>/edit/', views.edit_template, name='edit_template'),
    path('panel/text-templates/<int:template_id>/delete/', views.delete_template, name='delete_template'),
    path('template/create/', views.create_template, name='create_template'),
    path('panel/titles/', views.manage_titles, name='manage_titles'),
    path('panel/titles/create/', views.create_title, name='create_title'),
    path('panel/titles/<int:title_id>/edit/', views.edit_title, name='edit_title'),
    path('panel/titles/<int:title_id>/delete/', views.delete_title, name='delete_title'),
    path('panel/users/<int:user_id>/titles/', views.manage_user_titles, name='manage_user_titles'),
    path('templates/litvininkov/', views.public_templates, name='public_templates'),
    path('templates/litvininkov/<int:template_id>/edit/', views.edit_public_template, name='edit_public_template'),
    path('templates/litvininkov/<int:template_id>/delete/', views.delete_public_template, name='delete_public_template'),
    path('panel/generate-backup/', views.generate_backup, name='generate_backup'),
    path('panel/users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('panel/users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    path('stories/', views.story_list, name='story_list'),
    path('stories/create/', views.create_story, name='create_story'),
    path('stories/<int:pk>/', views.story_detail, name='story_detail'),
    path('stories/<int:pk>/edit/', views.edit_story, name='edit_story'),
    path('my-stories/', views.my_stories, name='my_stories'),
    path('story/<int:pk>/delete/', views.delete_story, name='delete_story'),
    path('stories/search/', views.search_stories, name='search_stories'),
    path('lecture/create/', views.create_lecture, name='create_lecture'),
    path('lecture/<int:pk>/edit/', views.edit_lecture, name='edit_lecture'),
    path('lecture/<int:pk>/delete/', views.delete_lecture, name='delete_lecture'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Обработчики ошибок
def custom_404(request, exception):
    return render(request, 'blog/errors/404.html', status=404)

def custom_500(request):
    return render(request, 'blog/errors/500.html', status=500)

handler404 = 'blog.urls.custom_404'
handler500 = 'blog.urls.custom_500' 