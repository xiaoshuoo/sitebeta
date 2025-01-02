from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, Sum
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Category, Post, Profile, Tag, Comment, PostView, InviteCode, PageSettings, Title, TextTemplate, Story
from .forms import CustomUserCreationForm, ProfileForm, PostForm, CommentForm, StoryForm
import json
import os
from .cloudinary_storage import CustomCloudinaryStorage
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import random
import string
from django.db import connection
from django.core import serializers
from django.core.files.storage import default_storage
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
import shutil
from django.conf import settings
from django.contrib.auth.hashers import make_password
import logging
from django.views.generic import TemplateView
import cloudinary
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.template.defaultfilters import register
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.utils.html import escape
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from datetime import timedelta

# Настраиваем logger
logger = logging.getLogger(__name__)

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def trim(value):
    return value.strip()

class HomeView(TemplateView):
    template_name = 'blog/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем актуальную статистику
        context['total_posts'] = Post.objects.filter(is_published=True).count()
        context['total_users'] = User.objects.filter(is_active=True).count()
        context['total_views'] = PostView.objects.count()
        context['total_comments'] = Comment.objects.count()
        
        # Получаем посты с их миниатюрами
        posts = Post.objects.filter(is_published=True).order_by('-created_at')[:6]
        
        # Проверяем и создаем slug для постов, у которых его нет
        for post in posts:
            if not post.slug:
                post.slug = slugify(post.title)
                counter = 1
                temp_slug = post.slug
                while Post.objects.filter(slug=temp_slug).exists():
                    temp_slug = f"{post.slug}-{counter}"
                    counter += 1
                post.slug = temp_slug
                post.save()
                
        context['latest_posts'] = posts
        
        # Получаем категории с количеством постов
        context['categories'] = Category.objects.annotate(
            total_posts=Count('post', filter=Q(post__is_published=True))
        ).order_by('-total_posts')
        
        # Получаем теги с количеством постов
        context['tags'] = Tag.objects.annotate(
            total_posts=Count('post', filter=Q(post__is_published=True))
        ).order_by('-total_posts')[:10]
        
        # Добавляем флаг для отображения админ-информации
        context['show_admin_info'] = self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        )
        
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'blog/profile_edit.html'
    success_url = reverse_lazy('blog:profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['profile'] = profile
        context['user'] = self.request.user
        
        # Добавляем отладочную информацию
        context['debug'] = True
        if profile.avatar and hasattr(profile.avatar, 'public_id'):
            context['debug_avatar'] = {
                'name': profile.avatar.public_id,
                'url': profile.avatar.url if hasattr(profile.avatar, 'url') else None,
                'resource_type': profile.avatar.resource_type if hasattr(profile.avatar, 'resource_type') else None,
                'format': profile.avatar.format if hasattr(profile.avatar, 'format') else None
            }
        if profile.cover and hasattr(profile.cover, 'public_id'):
            context['debug_cover'] = {
                'name': profile.cover.public_id,
                'url': profile.cover.url if hasattr(profile.cover, 'url') else None,
                'resource_type': profile.cover.resource_type if hasattr(profile.cover, 'resource_type') else None,
                'format': profile.cover.format if hasattr(profile.cover, 'format') else None
            }
        return context

    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)
            
            def process_image(image_file, max_size=(1920, 1080)):
                # Открываем изображение
                img = Image.open(image_file)
                
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Изменяем размер, сохраняя пропорции
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Сохраняем в буфер с оптимизацией
                output = BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                return output
            
            # Проверяем размер файлов перед загрузкой
            if 'cover' in self.request.FILES:
                cover_file = self.request.FILES['cover']
                if cover_file.size > 10 * 1024 * 1024:  # 10MB
                    # Обрабатываем изображение
                    processed_cover = process_image(cover_file, max_size=(1920, 1080))
                    try:
                        # Загружаем обработанное изображение
                        upload_result = cloudinary.uploader.upload(
                            processed_cover,
                            folder='covers/',
                            transformation={
                                'quality': 'auto:good',
                                'fetch_format': 'auto'
                            }
                        )
                        self.object.cover = upload_result['public_id']
                    except Exception as e:
                        logger.error(f"Error uploading cover: {str(e)}")
                        messages.error(self.request, 'Ошибка при загрузке оложки')
                        return self.form_invalid(form)
                else:
                    self.object.cover = cover_file
            
            if 'avatar' in self.request.FILES:
                avatar_file = self.request.FILES['avatar']
                if avatar_file.size > 5 * 1024 * 1024:  # 5MB
                    # Обрабатываем изображение
                    processed_avatar = process_image(avatar_file, max_size=(800, 800))
                    try:
                        # Загружаем обаботанное изображение
                        upload_result = cloudinary.uploader.upload(
                            processed_avatar,
                            folder='avatars/',
                            transformation={
                                'quality': 'auto:good',
                                'fetch_format': 'auto'
                            }
                        )
                        self.object.avatar = upload_result['public_id']
                    except Exception as e:
                        logger.error(f"Error uploading avatar: {str(e)}")
                        messages.error(self.request, 'Ошибка при загрузке аватара')
                        return self.form_invalid(form)
                else:
                    self.object.avatar = avatar_file
            
            self.object.save()
            messages.success(self.request, 'Профиль успешно обновлен')
            return super().form_valid(form)
            
        except Exception as e:
            logger.error(f"Form validation error: {str(e)}")
            messages.error(self.request, f'Ошибка при обновлении профиля: {str(e)}')
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        # Убираем сообщение о успешном обновлении при загрузке страницы
        return super().get(request, *args, **kwargs)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def upload_image(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']
        # Сохраняем файл через CustomCloudinaryStorage
        storage = CustomCloudinaryStorage()
        filename = storage.save(f'posts/content/{upload.name}', upload)
        url = storage.url(filename)
        return JsonResponse({
            'url': url,
            'uploaded': '1',
            'fileName': upload.name
        })
    return JsonResponse({'error': {'message': 'Ошибка загрузки файла'}}, status=400)

def check_page_status(page_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Проверяем статус страницы
            page_settings = PageSettings.objects.get_or_create(
                page_name=page_name,
                defaults={'is_active': True}
            )[0]
            
            if not page_settings.is_active:
                # Вместо редиректа рендерим страницу-заглушку
                return render(request, 'blog/page_disabled.html')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@check_page_status('contacts')
def contacts(request):
    """Страница контактов"""
    return render(request, 'blog/contacts.html')

@check_page_status('about')
def about(request):
    """Страница 'О сайте'"""
    return render(request, 'blog/about.html')

@check_page_status('create_post')
@login_required
def create_post(request):
    """Создание нового поста"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                post.is_published = True
                
                # Создаем slug из заголовка
                if not post.slug:
                    post.slug = slugify(post.title)
                    counter = 1
                    temp_slug = post.slug
                    while Post.objects.filter(slug=temp_slug).exists():
                        temp_slug = f"{post.slug}-{counter}"
                        counter += 1
                    post.slug = temp_slug
                
                # Обработка миниатюры
                if 'thumbnail' in request.FILES:
                    try:
                        thumbnail_file = request.FILES['thumbnail']
                        
                        # Загружаем изображение в Cloudinary
                        upload_result = cloudinary.uploader.upload(
                            thumbnail_file,
                            folder='thumbnails/',
                            resource_type='auto',
                            allowed_formats=['jpg', 'jpeg', 'png', 'gif'],
                            transformation={
                                'quality': 'auto:good',
                                'fetch_format': 'auto'
                            }
                        )
                        post.thumbnail = upload_result['public_id']
                        
                    except cloudinary.exceptions.Error as e:
                        logger.error(f"Cloudinary upload error: {str(e)}")
                        messages.error(request, 'Ошибка при загрузке изображения в облако')
                        return render(request, 'blog/post_form.html', {
                            'form': form,
                            'action': 'create',
                            'categories': Category.objects.all().order_by('name'),
                            'tags': Tag.objects.all().order_by('name')
                        })
                    except Exception as e:
                        logger.error(f"Error processing thumbnail: {str(e)}")
                        messages.error(request, 'Ошибка при обработке миниатюры')
                        return render(request, 'blog/post_form.html', {
                            'form': form,
                            'action': 'create',
                            'categories': Category.objects.all().order_by('name'),
                            'tags': Tag.objects.all().order_by('name')
                        })
                
                # Сохраняем пост
                post.save()
                form.save_m2m()  # Сохраняем теги
                messages.success(request, 'Пост успешно создан и опубликован!')
                return redirect('blog:post_detail', slug=post.slug)
                
            except Exception as e:
                logger.error(f"Error saving post: {str(e)}")
                messages.error(request, f'Ошибка при сохранении поста: {str(e)}')
                return render(request, 'blog/post_form.html', {
                    'form': form,
                    'action': 'create',
                    'categories': Category.objects.all().order_by('name'),
                    'tags': Tag.objects.all().order_by('name')
                })
        else:
            # Если форма невалидна, показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле {field}: {error}')
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'action': 'create',
        'categories': Category.objects.all().order_by('name'),
        'tags': Tag.objects.all().order_by('name')
    })

@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    context = {
        'post': post,
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
def edit_post(request, slug):
    logger.info(f"Trying to edit post with slug: {slug}")
    logger.info(f"Current user: {request.user.username}")
    
    post = get_object_or_404(Post, slug=slug)
    
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования этого поста')
        return redirect('blog:post_detail', slug=slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            if 'thumbnail' in request.FILES:
                try:
                    # Удаляем старую миниатюру если она есть
                    if post.thumbnail and hasattr(post.thumbnail, 'public_id'):
                        cloudinary.uploader.destroy(post.thumbnail.public_id)
                    
                    # Загружаем новую миниатюру
                    thumbnail_file = request.FILES['thumbnail']
                    upload_result = cloudinary.uploader.upload(
                        thumbnail_file,
                        folder='thumbnails/',
                        resource_type='auto'
                    )
                    post.thumbnail = upload_result['public_id']
                except Exception as e:
                    logger.error(f"Error processing thumbnail: {str(e)}")
                    messages.error(request, 'Ошибка при обработке миниатюры')
                    return render(request, 'blog/post_form.html', {
                        'form': form,
                        'post': post,
                        'action': 'edit',
                        'categories': Category.objects.all().order_by('name'),
                        'tags': Tag.objects.all().order_by('name')
                    })
            
            post.save()
            form.save_m2m()  # Сохраняем теги
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {
        'form': form, 
        'post': post, 
        'action': 'edit',
        'categories': Category.objects.all().order_by('name'),
        'tags': Tag.objects.all().order_by('name'),
        'debug': True,
        'debug_info': {
            'post_id': post.id,
            'post_slug': post.slug,
            'author': post.author.username,
            'current_user': request.user.username,
            'category': post.category.name if post.category else None,
            'tags': [tag.name for tag in post.tags.all()],
            'thumbnail': {
                'url': post.get_thumbnail_url() if post.thumbnail else None,
                'public_id': post.thumbnail.public_id if hasattr(post.thumbnail, 'public_id') else None
            }
        }
    })

@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        try:
            # Удаляем минитюру из Cloudinary если она есть
            if post.thumbnail and hasattr(post.thumbnail, 'public_id'):
                try:
                    cloudinary.uploader.destroy(post.thumbnail.public_id)
                except Exception as e:
                    logger.error(f"Error deleting thumbnail: {str(e)}")
            
            # Удаляем пост
            post.delete()
            messages.success(request, 'Пост успешно удален!')
            return redirect('blog:my_posts')
        except Exception as e:
            logger.error(f"Error deleting post: {str(e)}")
            messages.error(request, f'Ошибка при удалении поста: {str(e)}')
            return redirect('blog:post_detail', slug=slug)
    
    # Показываем страницу подтверждения
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', slug=slug)
    return redirect('blog:post_detail', slug=slug)

def categories_list(request):
    # Изменим имя аннотации на total_posts вместо posts_count
    categories = Category.objects.annotate(total_posts=Count('post'))
    
    context = {
        'categories': categories,
        'total_categories': categories.count(),
    }
    return render(request, 'blog/categories.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, is_published=True)
    return render(request, 'blog/category_detail.html', {'category': category, 'posts': posts})

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, is_published=True)
    return render(request, 'blog/tag_detail.html', {'tag': tag, 'posts': posts})

@login_required
def profile(request):
    user = request.user
    profile = user.profile
    
    context = {
        'profile': profile,
        'viewed_user': user,
        'posts': Post.objects.filter(author=user).order_by('-created_at'),
        'total_posts': Post.objects.filter(author=user).count(),
        'total_views': PostView.objects.filter(post__author=user).count(),
        'total_comments': Comment.objects.filter(post__author=user).count(),
        'debug': True,
        'debug_info': {
            'avatar': {
                'name': profile.avatar if profile.avatar else None,
                'url': profile.avatar if profile.avatar else None,
            },
            'cover': {
                'name': profile.cover if profile.cover else None,
                'url': profile.cover if profile.cover else None,
            }
        }
    }
    
    return render(request, 'blog/profile.html', context)

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'blog/user_profile.html', {'profile_user': user})

@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    total_views = sum(post.views_count for post in posts)
    
    context = {
        'posts': posts,
        'total_views': total_views,
    }
    return render(request, 'blog/my_posts.html', context)

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    """Админ панель"""
    # Получаем статистику
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_views = Post.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    # Получаем последние действия
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_posts = Post.objects.order_by('-created_at')[:5]
    recent_comments = Comment.objects.order_by('-created_date')[:5]
    
    # Получаем настройки страниц
    page_settings = PageSettings.objects.all()
    page_settings_dict = {settings.page_name: settings for settings in page_settings}
    
    # Получаем инвайт-коды
    invite_codes = InviteCode.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Получаем текстовые шаблоны
    templates = TextTemplate.objects.filter(created_by=request.user).order_by('-created_at')[:6]
    
    # Получаем информацию о базе данных
    try:
        with connection.cursor() as cursor:
            # Получаем размер базы данных
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            db_size = cursor.fetchone()[0]
            
            # Получаем количество таблиц
            cursor.execute("""
                SELECT count(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables_count = cursor.fetchone()[0]
            
            database_info = {
                'connected': True,
                'size': db_size,
                'tables_count': tables_count,
                'error': None
            }
    except Exception as e:
        database_info = {
            'connected': False,
            'size': 'N/A',
            'tables_count': 0,
            'error': str(e)
        }
    
    context = {
        'stats': {
            'users': {
                'total': total_users,
                'active': User.objects.filter(is_active=True).count(),
                'new': User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
            },
            'posts': {
                'total': total_posts,
                'published': Post.objects.filter(is_published=True).count(),
                'draft': Post.objects.filter(is_published=False).count()
            },
            'comments': {
                'total': total_comments
            },
            'views': {
                'total': total_views
            }
        },
        'database': database_info,
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_views': total_views,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'page_settings': page_settings_dict,
        'invite_codes': invite_codes,
        'templates': templates,
    }
    
    return render(request, 'blog/admin_panel.html', context)

@login_required
@require_POST
def update_profile_cover(request):
    """Обновление обложки профиля"""
    try:
        if 'cover' in request.FILES:
            profile = request.user.profile
            
            # Удаляем старую обложку если она есть
            if profile.cover:
                try:
                    cloudinary.uploader.destroy(profile.cover.public_id)
                    logger.info(f"Old cover deleted: {profile.cover.public_id}")
                except Exception as e:
                    logger.error(f"Error deleting old cover: {str(e)}")
            
            # Сохраняем новую обложку
            try:
                profile.cover = request.FILES['cover']
                profile.save()
                logger.info(f"New cover uploaded: {profile.cover.public_id}")
                
                return JsonResponse({
                    'success': True,
                    'url': profile.cover.url,
                    'debug': {
                        'public_id': profile.cover.public_id,
                        'url': profile.cover.url,
                        'resource_type': profile.cover.resource_type
                    }
                })
            except Exception as e:
                logger.error(f"Error uploading new cover: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Ошибка при загрузке обложки: {str(e)}'
                })
        
        return JsonResponse({
            'success': False,
            'error': 'Файл не был загружен'
        })
    except Exception as e:
        logger.error(f"Error updating cover: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_POST
def update_profile_avatar(request):
    """Обновление аватара профиля"""
    try:
        if 'avatar' in request.FILES:
            profile = request.user.profile
            
            # Удаляем старый аватар если он есть
            if profile.avatar:
                storage = CustomCloudinaryStorage()
                storage.delete(profile.avatar.name)
            
            # Сохраняем новый аватар
            profile.avatar = request.FILES['avatar']
            profile.save()
            
            return JsonResponse({
                'success': True,
                'url': profile.avatar.url
            })
        return JsonResponse({
            'success': False,
            'error': 'Файл не был загружен'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_POST
def remove_profile_cover(request):
    """даление обложки профиля"""
    try:
        profile = request.user.profile
        if profile.cover:
            storage = CustomCloudinaryStorage()
            storage.delete(profile.cover.name)
            profile.cover = None
            profile.save()
            
        return JsonResponse({
            'success': True
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@staff_member_required
def clear_cache(request):
    """Очистк кэша"""
    try:
        cache.clear()
        messages.success(request, 'Кэш успешно очищен')
    except Exception as e:
        messages.error(request, f'Ошибка при очистке кэша: {str(e)}')
    return redirect('blog:admin_panel')

@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """Включение/отключение пользователя"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            # Не позволяем блокировать администраторов
            if not user.is_staff:
                user.is_active = not user.is_active
                user.save()
                status = 'активирован' if user.is_active else 'заблокирован'
                messages.success(request, f'Пользователь {user.username} {status}')
            else:
                messages.error(request, 'Невозможно заблокировать администратора')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
    return redirect('blog:admin_panel')

@login_required
@user_passes_test(is_admin)
def reset_user_password(request, user_id):
    """Сброс пароля пользователя"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            # Генерируем случайный пароль
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            user.set_password(new_password)
            user.save()
            messages.success(
                request,
                f'Новый пароль для пользователя {user.username}: {new_password}'
            )
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
    return redirect('blog:admin_panel')

@staff_member_required
def create_invite(request):
    """Создание инвайт-кода"""
    try:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        invite = InviteCode.objects.create(
            code=code,
            created_by=request.user
        )
        messages.success(request, f'Создан инвайт-код: {code}')
    except Exception as e:
        messages.error(request, f'Ошибка при создании инвайт-кода: {str(e)}')
    return redirect('blog:admin_panel')

@staff_member_required
def deactivate_invite(request, code):
    """Деактивация инвайт-кода"""
    try:
        invite = InviteCode.objects.get(code=code)
        invite.is_active = False
        invite.save()
        messages.success(request, f'Инвайт-код {code} деактивирован')
    except InviteCode.DoesNotExist:
        messages.error(request, 'Инвайт-код не найден')
    except Exception as e:
        messages.error(request, f'Ошибка при деактивации кода: {str(e)}')
    return redirect('blog:admin_panel')

@staff_member_required
@require_POST
@csrf_exempt
def toggle_page_status(request, page_name):
    """Включение/отключение страницы"""
    if request.method == 'POST':
        try:
            page_setting = PageSettings.objects.get(page_name=page_name)
            page_setting.is_active = not page_setting.is_active
            page_setting.save()
            status = 'включена' if page_setting.is_active else 'отключена'
            messages.success(request, f'Страница {page_setting.get_page_name_display()} {status}')
        except PageSettings.DoesNotExist:
            messages.error(request, 'Страница не найдена')
    return redirect('blog:admin_panel')

@staff_member_required
def invite_codes(request):
    """Список инвайт-кодов"""
    codes = InviteCode.objects.all().order_by('-created_at')
    return render(request, 'blog/invite_codes.html', {'codes': codes})

@staff_member_required
def create_custom_invite(request):
    """Создание кастомного инвайт-кода"""
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            InviteCode.objects.create(code=code, created_by=request.user)
            messages.success(request, f'Создан инвайт-код: {code}')
        except Exception as e:
            messages.error(request, f'Ошибка при создании инвай-коа: {str(e)}')
    return redirect('blog:invite_codes')

@staff_member_required
def update_activity(request):
    """Обновление времени последней активности"""
    if request.method == 'POST':
        request.user.profile.last_seen = timezone.now()
        request.user.profile.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def set_offline(request):
    """Установка статуса оффлайн"""
    if request.method == 'POST':
        request.user.profile.last_seen = timezone.now() - timezone.timedelta(minutes=5)
        request.user.profile.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def health_check(request):
    """Проверка здоровья приложения"""
    try:
        # Проверяем подключение к БД
        connection.ensure_connection()
        # Проверяем работу кэша
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        return JsonResponse({'status': 'healthy'})
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=500)

@staff_member_required
def generate_backup(request):
    """Создание резервной копии данных"""
    try:
        # Получаем данные для бэкапа
        users = list(User.objects.values())
        posts = list(Post.objects.values())
        categories = list(Category.objects.values())
        tags = list(Tag.objects.values())

        # Формируем данные бэкапа
        backup_data = {
            'users': users,
            'posts': posts,
            'categories': categories,
            'tags': tags,
            'generated_at': datetime.now().isoformat()
        }

        # Создаем JSON-файл
        response = HttpResponse(
            json.dumps(backup_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
    except Exception as e:
        messages.error(request, f'Ошибка при создании бэкапа: {str(e)}')
        return redirect('blog:admin_panel')

@staff_member_required
def restore_database(request):
    """Восстановление базы данных из резервной копии"""
    if request.method == 'POST' and request.FILES.get('backup_file'):
        try:
            backup_file = request.FILES['backup_file']
            data = json.load(backup_file)

            # чищаем существующие данные
            PostView.objects.all().delete()
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

            # Восстанавливаем данные
            for model_name, items in data.items():
                if model_name == 'users':
                    for item in items:
                        if not User.objects.filter(username=item['fields']['username']).exists():
                            User.objects.create(**item['fields'])
                elif model_name == 'profiles':
                    for item in items:
                        Profile.objects.create(**item['fields'])
                # ... и та далее для каждой модели

            messages.success(request, 'База данных успешно восстановлена')
        except Exception as e:
            messages.error(request, f'Оибка при восстановлении базы данных: {str(e)}')
        
        return redirect('blog:admin_panel')
    
    return render(request, 'blog/restore_database.html')

@staff_member_required
def restore_media(request):
    """Восстановление медиа-файлов из бэкапа"""
    try:
        # Восстанавливаем файлы и бэкапа
        for dir_name in ['avatars', 'posts', 'thumbnails', 'covers']:
            backup_path = os.path.join(settings.MEDIA_BACKUP_ROOT, dir_name)
            media_path = os.path.join(settings.MEDIA_ROOT, dir_name)
            
            # Сздаем директорию если её нет
            os.makedirs(media_path, exist_ok=True)
            
            # Копируем файлы
            for filename in os.listdir(backup_path):
                src = os.path.join(backup_path, filename)
                dst = os.path.join(media_path, filename)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
        
        messages.success(request, 'Медиа-файлы успешно восстановлены')
    except Exception as e:
        messages.error(request, f'Ошибка при восстанвлении медиа-файлов: {str(e)}')
    
    return redirect('blog:admin_panel')

@staff_member_required
def reset_user_password(request, user_id):
    """Сброс пароля пользователя"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            # Генерируем случайный пароль
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            user.set_password(new_password)
            user.save()
            messages.success(
                request,
                f'Новый пароль для пользователя {user.username}: {new_password}'
            )
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
    return redirect('blog:admin_panel')

@staff_member_required
def bulk_user_action(request):
    """Массовые дйствия с пользователями"""
    if request.method == 'POST':
        user_ids = request.POST.getlist('users')
        action = request.POST.get('action')
        
        try:
            users = User.objects.filter(id__in=user_ids)
            if action == 'activate':
                users.update(is_active=True)
                messages.success(request, 'Выбранные пользователи акивированы')
            elif action == 'deactivate':
                users.update(is_active=False)
                messages.success(request, 'Выбранные ользователи деактивированы')
            elif action == 'delete':
                users.delete()
                messages.success(request, 'Выбранные пользователи удалены')
        except Exception as e:
            messages.error(request, f'Ошибка при выполнении действия: {str(e)}')
    
    return redirect('blog:admin_panel')

@staff_member_required
def bulk_post_action(request):
    """Массовые действия с постами"""
    if request.method == 'POST':
        post_ids = request.POST.getlist('posts')
        action = request.POST.get('action')
        
        try:
            posts = Post.objects.filter(id__in=post_ids)
            if action == 'publish':
                posts.update(is_published=True)
                messages.success(request, 'Выбраные посты опубликованы')
            elif action == 'unpublish':
                posts.update(is_published=False)
                messages.success(request, 'Выбранные посты сняты с публикации')
            elif action == 'delete':
                posts.delete()
                messages.success(request, 'Выбранные посты удалены')
        except Exception as e:
            messages.error(request, f'Ошибка при выполнении действия: {str(e)}')
    
    return redirect('blog:admin_panel')

@staff_member_required
def generate_report(request):
    """Генерация отчета о состоянии сайта"""
    try:
        report = {
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'inactive': User.objects.filter(is_active=False).count()
            },
            'posts': {
                'total': Post.objects.count(),
                'published': Post.objects.filter(is_published=True).count(),
                'drafts': Post.objects.filter(is_published=False).count()
            },
            'comments': Comment.objects.count(),
            'categories': Category.objects.count(),
            'tags': Tag.objects.count()
        }
        
        return JsonResponse(report)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def clean_database(request):
    """Очистка азы днных от неиспоьземых данных"""
    try:
        # Удаляем неиспользуемые теги
        Tag.objects.filter(post=None).delete()
        
        # Удаляем старые просмотры
        old_views = PostView.objects.filter(
            timestamp__lt=timezone.now() - timezone.timedelta(days=30)
        )
        old_views.delete()
        
        # Удаляем неактивные инвайт-коды
        InviteCode.objects.filter(
            is_active=False, 
            created_at__lt=timezone.now() - timezone.timedelta(days=30)
        ).delete()
        
        messages.success(request, 'База данных успешно очищена')
    except Exception as e:
        messages.error(request, f'Ошибка при очистке базы данных: {str(e)}')
    
    return redirect('blog:admin_panel')

@staff_member_required
def manage_titles(request):
    """Управление титулами"""
    titles = Title.objects.all().order_by('name')
    return render(request, 'blog/admin/manage_titles.html', {'titles': titles})

@staff_member_required
def create_title(request):
    """Создание нового титула"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            color = request.POST.get('color', '#8B5CF6')
            icon = request.POST.get('icon', 'fas fa-award')
            
            Title.objects.create(
                name=name,
                description=description,
                color=color,
                icon=icon
            )
            messages.success(request, 'Титул успешно создан')
        except Exception as e:
            messages.error(request, f'Ошибка пи создании титула: {str(e)}')
    return redirect('blog:manage_titles')

@staff_member_required
def edit_title(request, title_id):
    """Редактирование титула"""
    title = get_object_or_404(Title, id=title_id)
    if request.method == 'POST':
        try:
            title.name = request.POST.get('name')
            title.description = request.POST.get('description')
            title.color = request.POST.get('color')
            title.icon = request.POST.get('icon')
            title.save()
            messages.success(request, 'Титул успешно обновлен')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлени титула: {str(e)}')
        return redirect('blog:manage_titles')
    return render(request, 'blog/admin/edit_title.html', {'title': title})

@staff_member_required
def delete_title(request, title_id):
    """Удаление титула"""
    try:
        title = Title.objects.get(id=title_id)
        title.delete()
        messages.success(request, 'Титул успешно удален')
    except Title.DoesNotExist:
        messages.error(request, 'Титул не найден')
    except Exception as e:
        messages.error(request, f'Ошибка при удалении титула: {str(e)}')
    return redirect('blog:manage_titles')

@staff_member_required
def manage_user_titles(request, user_id):
    """Управление титулами пользователя"""
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        try:
            title_ids = request.POST.getlist('titles')
            user.profile.titles.clear()
            user.profile.titles.add(*title_ids)
            messages.success(request, f'Титулы пользователя {user.username} обновлены')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении титулов: {str(e)}')
        return redirect('blog:admin_panel')
    
    available_titles = Title.objects.all()
    return render(request, 'blog/admin/manage_user_titles.html', {
        'user': user,
        'available_titles': available_titles
    })

@staff_member_required
def text_templates(request):
    """Список шаблонов текстов"""
    templates = TextTemplate.objects.filter(created_by=request.user).order_by('category', 'title')
    return render(request, 'blog/admin/text_templates.html', {'templates': templates})

@staff_member_required
def edit_template(request, template_id):
    """Редактирование шаблона текста"""
    template = get_object_or_404(TextTemplate, id=template_id, created_by=request.user)
    
    if request.method == 'POST':
        try:
            template.title = request.POST.get('title')
            template.content = request.POST.get('content')
            template.category = request.POST.get('category')
            template.save()
            messages.success(request, 'Шаблон успешно обновлен')
            return redirect('blog:text_templates')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении шаблона: {str(e)}')
    
    return render(request, 'blog/admin/edit_template.html', {
        'template': template,
        'title': 'Редактирование шаблона'
    })

@staff_member_required
def delete_template(request, template_id):
    """Удаление шаблона"""
    template = get_object_or_404(TextTemplate, id=template_id, created_by=request.user)
    
    if request.method == 'POST':
        try:
            template.delete()
            messages.success(request, 'Шаблон успешно удален')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении шаблона: {str(e)}')
    
    return redirect('blog:text_templates')

@staff_member_required
def create_template(request):
    """Создание нового шаблона"""
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')
            category = request.POST.get('category')
            
            TextTemplate.objects.create(
                title=title,
                content=content,
                category=category,
                created_by=request.user  # Явно указываем текущего пользователя
            )
            messages.success(request, 'Шаблон успешно создан')
        except Exception as e:
            messages.error(request, f'Ошибка при создании шаблона: {str(e)}')
    return redirect('blog:text_templates')

def search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    
    print(f"Search request received - Query: {query}, Type: {search_type}")  # Отладочная информация
    
    if not query or len(query) < 2:
        print("Query too short or empty")  # Отладочная информация
        return JsonResponse({'results': []})
    
    results = []
    
    if search_type in ['all', 'posts']:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct().order_by('-created_at')[:5]
        
        print(f"Found {posts.count()} posts")  # Отладочная информация
        
        for post in posts:
            # Находим контекст для подсветки
            content = post.content
            start_idx = content.lower().find(query.lower())
            if start_idx != -1:
                start = max(0, start_idx - 50)
                end = min(len(content), start_idx + len(query) + 50)
                highlight = '...' + escape(content[start:end]) + '...'
            else:
                highlight = escape(content[:100]) + '...'

            results.append({
                'type': 'post',
                'icon': 'fa-file-alt',
                'title': escape(post.title),
                'url': reverse('blog:post_detail', kwargs={'slug': post.slug}),
                'subtitle': f'В категории {escape(post.category.name)}',
                'highlight': highlight
            })
    
    if search_type in ['all', 'categories']:
        categories = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()[:3]
        
        print(f"Found {categories.count()} categories")  # Отладочная информация
        
        for category in categories:
            post_count = category.posts.count()
            results.append({
                'type': 'category',
                'icon': 'fa-folder',
                'title': escape(category.name),
                'url': reverse('blog:category_detail', kwargs={'slug': category.slug}),
                'subtitle': f'{post_count} {post_count % 10 == 1 and post_count % 100 != 11 and "пост" or "постов"}',
                'highlight': escape(category.description[:100]) if category.description else ''
            })
    
    if search_type in ['all', 'tags']:
        tags = Tag.objects.filter(name__icontains=query).distinct()[:5]
        
        print(f"Found {tags.count()} tags")  # Отладочная информация
        
        for tag in tags:
            post_count = tag.posts.count()
            results.append({
                'type': 'tag',
                'icon': 'fa-tag',
                'title': escape(tag.name),
                'url': reverse('blog:tag_detail', kwargs={'slug': tag.slug}),
                'subtitle': f'{post_count} {post_count % 10 == 1 and post_count % 100 != 11 and "пост" or "постов"}',
                'highlight': ''
            })
    
    print(f"Total results: {len(results)}")  # Отладочная информация
    
    response_data = {
        'results': results,
        'query': query,
        'total': len(results)
    }
    print(f"Sending response: {response_data}")  # Отладочная информация
    
    return JsonResponse(response_data)

def post_list(request):
    """Список всех постов"""
    posts = Post.objects.filter(is_published=True)
    return render(request, 'blog/post_list.html', {'posts': posts})

def public_templates(request):
    """Публичная страница шаблонов (без авторизации)"""
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')
            category = request.POST.get('category', 'general')
            
            # Создаем публичный шаблон (без автора)
            TextTemplate.objects.create(
                title=title,
                content=content,
                category=category,
                created_by=None  # Явно указываем, что это публичный шаблон
            )
            messages.success(request, 'Шаблон успешно создан')
        except Exception as e:
            messages.error(request, f'Ошибка при создании шаблона: {str(e)}')
    
    # Получаем только публичные шаблоны (без автора)
    templates = TextTemplate.objects.filter(created_by=None).order_by('-created_at')
    return render(request, 'blog/public_templates.html', {
        'templates': templates,
        'categories': TextTemplate.objects.filter(created_by=None).values_list('category', flat=True).distinct()
    })

def edit_public_template(request, template_id):
    """Редактирование публичного шаблона"""
    # Получаем только публичный шаблон
    template = get_object_or_404(TextTemplate, id=template_id, created_by=None)
    
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')
            category = request.POST.get('category', 'general')
            
            template.title = title
            template.content = content
            template.category = category
            template.save()
            
            messages.success(request, 'Шаблон успешно обновлен')
            return redirect('blog:public_templates')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении шаблона: {str(e)}')
    
    return render(request, 'blog/edit_public_template.html', {'template': template})

def delete_public_template(request, template_id):
    """Удаление публичного шаблона"""
    # Получаем только публичный шаблон
    template = get_object_or_404(TextTemplate, id=template_id, created_by=None)
    
    if request.method == 'POST':
        try:
            template.delete()
            messages.success(request, 'Шаблон успешно удален')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении шаблона: {str(e)}')
    
    return redirect('blog:public_templates')

@login_required
def create_story(request):
    """Создание новой истории"""
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.is_draft = 'is_draft' in request.POST
            story.save()
            form.save_m2m()  # Сохраняем теги
            messages.success(request, 'История успешно создана')
            return redirect('blog:story_detail', pk=story.pk)
    else:
        form = StoryForm()
    
    return render(request, 'blog/create_story.html', {'form': form})

@login_required
def edit_story(request, pk):
    """Редактирование истории"""
    story = get_object_or_404(Story, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            story = form.save(commit=False)
            story.is_draft = 'is_draft' in request.POST
            story.save()
            form.save_m2m()
            messages.success(request, 'История успешно обновлена')
            return redirect('blog:story_detail', pk=story.pk)
    else:
        form = StoryForm(instance=story)
        # Подготавливаем теги для формы
        form.initial['tags'] = ', '.join(tag.name for tag in story.tags.all())
    
    return render(request, 'blog/edit_story.html', {'form': form, 'story': story})

def story_detail(request, pk):
    """Просмотр истории"""
    story = get_object_or_404(Story, pk=pk)
    
    # Увеличиваем счетчик просмотров
    story.views_count += 1
    story.save()
    
    return render(request, 'blog/story_detail.html', {'story': story})

def story_list(request):
    """Список всех историй"""
    stories = Story.objects.filter(is_draft=False).order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(stories, 12)
    page = request.GET.get('page')
    stories = paginator.get_page(page)
    
    return render(request, 'blog/story_list.html', {'stories': stories})

@login_required
def my_stories(request):
    """Мои истории"""
    stories = Story.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'blog/my_stories.html', {'stories': stories})

@login_required
def delete_story(request, pk):
    story = get_object_or_404(Story, pk=pk)
    
    # Проверяем, является ли пользователь автором истории
    if request.user != story.author:
        messages.error(request, 'У вас нет прав для удаления этой истории.')
        return redirect('blog:story_detail', pk=pk)
    
    # Удаляем историю
    story.delete()
    messages.success(request, 'История успешно удалена.')
    return redirect('blog:stories')  # Перенаправляем на список историй

def search_stories(request):
    """Поиск историй по названию и тегам"""
    query = request.GET.get('q', '')
    tag = request.GET.get('tag', '')
    
    stories = Story.objects.filter(is_draft=False)
    
    if query:
        stories = stories.filter(
            Q(title__icontains=query) |
            Q(alt_titles__icontains=query) |
            Q(description__icontains=query)
        )
    
    if tag:
        stories = stories.filter(tags__name__icontains=tag)
    
    # Удаляем дубликаты, если они появились из-за поиска по нескольким полям
    stories = stories.distinct().order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(stories, 12)
    page = request.GET.get('page')
    stories = paginator.get_page(page)
    
    # Получаем популярные теги для облака тегов
    popular_tags = Tag.objects.annotate(
        stories_count=Count('story')
    ).filter(stories_count__gt=0).order_by('-stories_count')[:20]
    
    context = {
        'stories': stories,
        'query': query,
        'tag': tag,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'blog/search_stories.html', context)
