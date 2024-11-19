from django.urls import path
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from .views import ProfileUpdateView

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.post_delete, name='delete_post'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('categories/', views.categories_list, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/cover/', views.update_profile_cover, name='update_profile_cover'),
    path('profile/avatar/', views.update_profile_avatar, name='update_profile_avatar'),
    path('profile/cover/remove/', views.remove_profile_cover, name='remove_profile_cover'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('search/', views.search, name='search'),
    path('posts/', views.post_list, name='post_list'),
    path('panel/', views.admin_panel, name='admin_panel'),
    path('panel/clear-cache/', views.clear_cache, name='clear_cache'),
    path('panel/toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('invite/create/', views.create_invite, name='create_invite'),
    path('invite/list/', views.invite_codes, name='invite_codes'),
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
    path('admin/generate-backup/', views.generate_backup, name='generate_backup'),
    path('admin/reset-user-password/<int:user_id>/', views.reset_user_password, name='reset_user_password'),
    path('admin/toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/clear-cache/', views.clear_cache, name='clear_cache'),
    path('admin/bulk-user-action/', views.bulk_user_action, name='bulk_user_action'),
    path('admin/bulk-post-action/', views.bulk_post_action, name='bulk_post_action'),
    path('admin/generate-report/', views.generate_report, name='generate_report'),
    path('admin/clean-database/', views.clean_database, name='clean_database'),
    path('panel/toggle-page/<str:page_name>/', views.toggle_page_status, name='toggle_page_status'),
    path('panel/create-custom-invite/', views.create_custom_invite, name='create_custom_invite'),
    path('panel/deactivate-invite/<str:code>/', views.deactivate_invite, name='deactivate_invite'),
    path('admin/restore-database/', views.restore_database, name='restore_database'),
    path('panel/backup/', views.generate_backup, name='generate_backup'),
    path('panel/restore/', views.restore_database, name='restore_database'),
    path('health/', views.health_check, name='health'),
    path('panel/clear-database/', views.clear_database, name='clear_database'),
]

# Обработчики ошибок
def custom_404(request, exception):
    return render(request, 'blog/errors/404.html', status=404)

def custom_500(request):
    return render(request, 'blog/errors/500.html', status=500)

handler404 = 'blog.urls.custom_404'
handler500 = 'blog.urls.custom_500' 