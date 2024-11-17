from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Sum, Max, F
import random
import string
from .models import Post, Category, Tag, InviteCode, Profile, Comment, PostView, PageSettings
from .forms import PostForm, CustomUserCreationForm, ProfileUpdateForm
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.views.generic.edit import CreateView
from django.views.generic import ListView
import json
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.admin.models import LogEntry
from datetime import datetime
import os
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import shutil
from django.utils.text import slugify
import tempfile
from django.core import management
import time
from django.db import connection
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def calculate_streak_days(user):
    """Подсчет дней подряд с публикациями"""
    posts = Post.objects.filter(
        author=user,
        is_published=True
    ).order_by('-created_at')
    
    if not posts:
        return 0
        
    streak = 0
    current_date = timezone.now().date()
    last_post_date = None
    
    for post in posts:
        post_date = post.created_at.date()
        
        if last_post_date is None:
            last_post_date = post_date
            streak = 1
            continue
            
        # Если разница между постами больше 1 дня, прерыв подсчет
        if (last_post_date - post_date).days > 1:
            break
            
        streak += 1
        last_post_date = post_date
        
    return streak

def calculate_achievements(user):
    """Пчет достижений пользовател"""
    achievements = 0
    
    # Достижение за првый пост
    if Post.objects.filter(author=user, is_published=True).exists():
        achievements += 1
    
    # Дотижение за 10 постов
    if Post.objects.filter(author=user, is_published=True).count() >= 10:
        achievements += 1
    
    # Достижение за 100 просмотров
    total_views = Post.objects.filter(author=user).aggregate(
        total_views=models.Sum('views_count')
    )['total_views'] or 0
    if total_views >= 100:
        achievements += 1
    
    # Достижение за серию публикаций (3 дня подряд)
    if calculate_streak_days(user) >= 3:
        achievements += 1
    
    return achievements

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Генерируем уникальный slug
            base_slug = slugify(post.title)
            if not base_slug:
                base_slug = 'post'
            unique_slug = base_slug
            counter = 1
            while Post.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            post.slug = unique_slug
            
            try:
                post.save()
                form.save_m2m()  # Сохраняем связи many-to-many (теги)
                messages.success(request, 'Пост успешно создан!')
                return redirect('blog:post_detail', slug=post.slug)
            except Exception as e:
                print(f"Error saving post: {str(e)}")  # Для отладки
                messages.error(request, f'Ошибка при создании поста: {str(e)}')
        else:
            print(f"Form errors: {form.errors}")  # Для отладки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле {field}: {error}')
    else:
        form = PostForm()
    
    # Проверяем, включена ли страница создания постов
    try:
        page_settings = PageSettings.objects.get(page_name=PageSettings.CREATE_POST_PAGE)
        if not page_settings.is_active:
            return render(request, 'blog/page_disabled.html', {
                'message': page_settings.disabled_message
            })
    except PageSettings.DoesNotExist:
        pass

    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Создать пост',
        'button_text': 'Опубликовать'
    })

@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.content = form.cleaned_data['content']
            post.save()
            
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        # Инициаизируем форму с существующими данными
        initial_data = {
            'content': post.content,  # Добавляем контент в initial
        }
        form = PostForm(instance=post, initial=initial_data)
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'post': post,
        'title': 'Редактировать пост',
        'button_text': 'Сохранить изменения',
        'is_edit': True  # Флаг дл шаблона
    })

def post_detail(request, slug):
    # Получаем пост или возвращаем 404
    post = get_object_or_404(Post, slug=slug)
    
    # Увеличиваем счетчк просмотров только для уникальных пользователей
    if request.user.is_authenticated:
        # Для авторизованных пользователей используем их ID
        post_view, created = PostView.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'session_key': None}
        )
        if created:
            post.views_count += 1
            post.save()
    else:
        # Для анонимных пользователей используем сессию
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        try:
            # Пробуем найти просмотр по session_key
            PostView.objects.get(post=post, session_key=session_key)
        except PostView.DoesNotExist:
            # Есл просмотра ет, создаем новый
            PostView.objects.create(
                post=post,
                user=None,
                session_key=session_key
            )
            post.views_count += 1
            post.save()
    
    # Получаем похожие посты
    similar_posts = Post.objects.filter(
        category=post.category,
        is_published=True,
        slug__isnull=False
    ).exclude(
        id=post.id,
        slug=''
    ).order_by('-created_at')[:3]
    
    context = {
        'post': post,
        'similar_posts': similar_posts,
    }
    return render(request, 'blog/post_detail.html', context)

def home(request):
    context = {
        'posts': Post.objects.filter(is_published=True).order_by('-created_at'),
        'categories': Category.objects.annotate(
            posts_count=Count('posts')
        ).order_by('-posts_count')[:4],
        'top_authors': User.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__is_published=True)),
            total_views=Sum('posts__views_count', filter=Q(posts__is_published=True))
        ).filter(
            posts_count__gt=0
        ).select_related(
            'profile'
        ).prefetch_related(
            'posts'
        ).order_by('-posts_count')[:4],
        'trending_posts': Post.objects.filter(
            is_published=True
        ).annotate(
            comments_count=Count('comments')
        ).order_by('-views_count', '-comments_count')[:5],
        'popular_tags': Tag.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__is_published=True))
        ).filter(
            posts_count__gt=0
        ).order_by('-posts_count')[:12],
        'total_posts': Post.objects.filter(is_published=True).count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'total_comments': Comment.objects.count(),
        'total_views': Post.objects.aggregate(total_views=Sum('views_count'))['total_views'] or 0,
    }
    return render(request, 'blog/home.html', context)

def get_page_range(paginator, current_page, show_pages=2):
    """
    Возвращает дипазон страниц для отображения в пагинации
    show_pages определяе количество страниц до и после текущей
    """
    page_range = []
    
    # Всегда показываем первую страниц
    page_range.append(1)
    
    # Вычсляем диапазон страниц вокруг ущей
    start_page = max(2, current_page - show_pages)
    end_page = min(paginator.num_pages, current_page + show_pages)
    
    # Добавляем многоточие после первой страницы, если нужно
    if start_page > 2:
        page_range.append('...')
    
    # Добавляем страницы из диапазона
    page_range.extend(range(start_page, end_page + 1))
    
    # Добавляем многоточи перед последней страницей, если нужно
    if end_page < paginator.num_pages - 1:
        page_range.append('...')
    
    # Всегд показываем последюю страницу, если она не входит в диапазон
    if paginator.num_pages > 1 and paginator.num_pages not in page_range:
        page_range.append(paginator.num_pages)
    
    return page_range

def categories_list(request):
    # Фильтруе категории, исключая те, у которых не slug
    categories = Category.objects.exclude(slug__isnull=True).exclude(slug='')
    context = {
        'categories': categories,
    }
    return render(request, 'blog/categories.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, is_published=True).order_by('-created_at')
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category_detail.html', context)

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, is_published=True).order_by('-created_at')
    
    context = {
        'tag': tag,
        'posts': posts,
    }
    return render(request, 'blog/tag_detail.html', context)

@login_required
def about(request):
    if not request.user.is_staff:
        messages.error(request, "У вас нет прав для просмотра этой страницы")
        return redirect('blog:home')
    return render(request, 'blog/about.html')

@login_required
def profile(request):
    """Личный профиль пользователя"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    posts = Post.objects.filter(
        author=request.user
    ).exclude(
        slug=''
    ).select_related(
        'category'
    ).prefetch_related(
        'tags'
    ).order_by('-created_at')
    
    total_posts = posts.count()
    total_views = posts.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    # Добавляем новые данные
    streak_days = calculate_streak_days(request.user)
    last_activity = request.user.last_login or request.user.date_joined
    achievements_count = calculate_achievements(request.user)
    
    context = {
        'profile': profile,
        'viewed_user': request.user,
        'posts': posts,
        'total_posts': total_posts,
        'total_views': total_views,
        'streak_days': streak_days,
        'last_activity': last_activity,
        'achievements_count': achievements_count,
    }
    return render(request, 'blog/profile.html', context)

@login_required
def my_posts(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
    context = {
        'posts': user_posts,
        'title': 'Мои посты'
    }
    return render(request, 'blog/my_posts.html', context)

def generate_invite_code():
    """Генерация 8-символьного кода приглашеня"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@login_required
def create_invite(request):
    if not request.user.is_staff:
        messages.error(request, "У вс нет прав для создания приглашений")
        return redirect('blog:home')
    
    code = generate_invite_code()
    InviteCode.objects.create(code=code, created_by=request.user)
    messages.success(request, f"Создан код приглашения: {code}")
    return redirect('blog:invite_codes')

@login_required
def invite_codes(request):
    codes = InviteCode.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'blog/invite_codes.html', {'codes': codes})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Получаем и проверяем инвайт-код
                invite_code = form.cleaned_data['invite_code']
                invite = InviteCode.objects.get(code=invite_code, is_active=True)
                
                # Создаем пользователя
                user = form.save()
                
                # Используем инвайт-код
                invite.use(user)
                
                # Автоматически входим в систему
                login(request, user)
                
                # Создаем профиль пользователя (если не создался автоматически)
                Profile.objects.get_or_create(user=user)
                
                messages.success(request, 'Регистрация успешно завершена! Добро пожаловать!')
                return redirect('blog:home')  # Пеенаправляем на главную
                
            except InviteCode.DoesNotExist:
                messages.error(request, 'Недействительный инвайт-код')
            except Exception as e:
                messages.error(request, f'Ошибка при регистрации: {str(e)}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['avatar', 'bio', 'location', 'website', 'occupation', 'cover']
    template_name = 'blog/profile_form.html'
    success_url = reverse_lazy('blog:profile')

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        profile = form.save(commit=False)
        
        # Обработк аватара
        if 'avatar' in self.request.FILES:
            if profile.avatar:
                try:
                    profile.avatar.delete(save=False)
                except:
                    pass
            profile.avatar = self.request.FILES['avatar']
        
        # Обработка бложки
        if 'cover' in self.request.FILES:
            if profile.cover:
                try:
                    profile.cover.delete(save=False)
                except:
                    pass
            profile.cover = self.request.FILES['cover']
        
        # Сохраняем изменения
        try:
            profile.save()
            messages.success(self.request, 'Профиль успешно обновлен!')
        except Exception as e:
            messages.error(self.request, f'Ошибка при обновлении профиля: {str(e)}')
            return self.form_invalid(form)
            
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Поаста, исправьте ошибки в форме.')
        return super().form_invalid(form)

def user_profile(request, username):
    """Публичный профиль пользателя"""
    viewed_user = get_object_or_404(User, username=username)
    
    # Полчаем все опубликованные посты пользователя
    posts = Post.objects.filter(
        author=viewed_user,
        is_published=True
    ).select_related(
        'category'
    ).prefetch_related(
        'tags'
    ).order_by('-created_at')
    
    total_posts = posts.count()
    total_views = posts.aggregate(Sum('views_count'))['views_count__sum'] or 0
    comments_count = Comment.objects.filter(post__author=viewed_user).count()
    
    # Получае статистику
    streak_days = calculate_streak_days(viewed_user)
    achievements_count = calculate_achievements(viewed_user)
    
    context = {
        'viewed_user': viewed_user,  # Пользователь, чей профиь просматривают
        'profile': viewed_user.profile,
        'posts': posts,
        'total_posts': total_posts,
        'total_views': total_views,
        'comments_count': comments_count,
        'streak_days': streak_days,
        'achievements_count': achievements_count,
    }
    return render(request, 'blog/profile.html', context)

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален!')
        return redirect('blog:home')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

def get_database_info():
    """Получение базовой информации о базе данных"""
    try:
        # Создае�� прямое подключение к PostgreSQL
        conn = psycopg2.connect(
            dbname='django_blog_7f9a',
            user='django_blog_7f9a_user',
            password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
            host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
            port='5432',
            sslmode='require'
        )
        
        cursor = conn.cursor()

        # Получаем версию PostgreSQL
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]

        # Получаем список таблиц и их размеры
        cursor.execute("""
            SELECT 
                t.tablename as table_name,
                pg_size_pretty(pg_total_relation_size(quote_ident(t.tablename)::text)) as size,
                pg_total_relation_size(quote_ident(t.tablename)::text) as raw_size,
                (SELECT count(*) FROM information_schema.columns WHERE table_name=t.tablename) as columns_count,
                CASE 
                    WHEN t.tablename = 'auth_user' THEN (SELECT count(*) FROM auth_user)
                    WHEN t.tablename = 'blog_post' THEN (SELECT count(*) FROM blog_post)
                    WHEN t.tablename = 'blog_comment' THEN (SELECT count(*) FROM blog_comment)
                    WHEN t.tablename = 'blog_profile' THEN (SELECT count(*) FROM blog_profile)
                    WHEN t.tablename = 'blog_category' THEN (SELECT count(*) FROM blog_category)
                    ELSE 0
                END as records_count
            FROM pg_tables t
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(quote_ident(t.tablename)::text) DESC
        """)
        tables = cursor.fetchall()

        # Получаем статистику записей
        stats = {
            'users': 0,
            'posts': 0,
            'comments': 0,
            'profiles': 0,
            'categories': 0
        }

        # Подсчитываем записи в каждой таблице
        for table in tables:
            table_name = table[0]
            records = table[4]
            
            if table_name == 'auth_user':
                stats['users'] = records
            elif table_name == 'blog_post':
                stats['posts'] = records
            elif table_name == 'blog_comment':
                stats['comments'] = records
            elif table_name == 'blog_profile':
                stats['profiles'] = records
            elif table_name == 'blog_category':
                stats['categories'] = records

        # Получаем информацию о кэше и использовании памяти
        cursor.execute("""
            SELECT 
                sum(heap_blks_hit) * current_setting('block_size')::bigint as cache_hit_bytes,
                sum(heap_blks_read) * current_setting('block_size')::bigint as disk_read_bytes,
                sum(heap_blks_hit)::float / 
                    nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100 as cache_hit_ratio
            FROM pg_statio_user_tables;
        """)
        memory_stats = cursor.fetchone()

        # Получаем информацию о подключениях
        cursor.execute("""
            SELECT 
                count(*) as total,
                count(*) FILTER (WHERE state = 'active') as active,
                count(*) FILTER (WHERE state = 'idle') as idle
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)
        connections = cursor.fetchone()

        # Получаем общий размер базы данных
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        total_size = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {
            'connection_status': {
                'is_connected': True,
                'version': version,
            },
            'size': total_size,
            'tables': [
                {
                    'name': table[0],
                    'size': table[1],
                    'raw_size': table[2],
                    'columns': table[3],
                    'records': table[4]
                } for table in tables
            ],
            'stats': stats,
            'memory_usage': {
                'total_connections': connections[0] if connections else 0,
                'active_connections': connections[1] if connections else 0,
                'idle_connections': connections[2] if connections else 0,
                'cache_hit_size': f"{memory_stats[0]/1024/1024:.1f}MB" if memory_stats and memory_stats[0] else 'N/A',
                'disk_read_size': f"{memory_stats[1]/1024/1024:.1f}MB" if memory_stats and memory_stats[1] else 'N/A',
                'cache_hit_ratio': f"{memory_stats[2]:.1f}%" if memory_stats and memory_stats[2] else 'N/A',
                'total_size': total_size,
                'table_count': len(tables),
                'total_rows': sum(table[4] for table in tables)
            }
        }
    except Exception as e:
        print(f"Database info error: {str(e)}")  # Для отладки
        return {
            'error': str(e),
            'connection_status': {
                'is_connected': False,
                'version': 'Unknown'
            },
            'size': 'N/A',
            'tables': [],
            'stats': {
                'users': 0,
                'posts': 0,
                'comments': 0,
                'profiles': 0,
                'categories': 0
            },
            'memory_usage': {
                'total_connections': 0,
                'active_connections': 0,
                'idle_connections': 0,
                'cache_hit_size': 'N/A',
                'disk_read_size': 'N/A',
                'cache_hit_ratio': 'N/A',
                'total_size': 'N/A',
                'table_count': 0,
                'total_rows': 0
            }
        }

@staff_member_required
def admin_panel(request):
    # Добавляем определение thirty_days_ago
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Получаем активные инвайт-коды
    active_invites = InviteCode.objects.filter(is_active=True)
    
    # Получаем популярные категории с подсчетом постов через annotate
    popular_categories = Category.objects.annotate(
        total_posts=Count('posts')
    ).order_by('-total_posts')[:5]
    
    # Добавим полуение настроек страниц
    page_settings = {
        'contacts': PageSettings.objects.get_or_create(
            page_name=PageSettings.CONTACTS_PAGE,
            defaults={'updated_by': request.user}
        )[0],
        'create_post': PageSettings.objects.get_or_create(
            page_name=PageSettings.CREATE_POST_PAGE,
            defaults={'updated_by': request.user}
        )[0]
    }
    
    database_config = {
        'name': 'django_blog_7f9a',
        'host': 'dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
        'user': 'django_blog_7f9a_user',
        'engine': 'PostgreSQL',
        'version': get_database_info().get('version', 'Unknown')
    }
    
    context = {
        # Основная статистика
        'users_count': User.objects.count(),
        'posts_count': Post.objects.count(),
        'categories_count': Category.objects.count(),
        'comments_count': Comment.objects.count(),
        
        # Статистика активноти
        'new_users_month': User.objects.filter(date_joined__gte=thirty_days_ago).count(),
        'new_posts_month': Post.objects.filter(created_at__gte=thirty_days_ago).count(),
        'active_users_month': User.objects.filter(last_login__gte=thirty_days_ago).count(),
        'total_views': Post.objects.aggregate(total_views=Sum('views_count'))['total_views'] or 0,
        
        # Списки для управления
        'users': User.objects.all().order_by('-date_joined')[:10],
        'recent_posts': Post.objects.select_related('author', 'category').order_by('-created_at')[:10],
        'recent_comments': Comment.objects.select_related('author', 'post').order_by('-created_date')[:10],
        'active_invites': active_invites,
        'popular_categories': popular_categories,  # Используем аннотированный QuerySet
        
        # Логи и активность
        'recent_logs': LogEntry.objects.select_related('user', 'content_type')[:10],
        'user_activity': get_user_activity_stats(),
        'system_info': get_system_info(),
        'page_settings': page_settings,
        'database_info': get_database_info(),
        'database_config': database_config
    }
    return render(request, 'blog/admin_panel.html', context)

def get_user_activity_stats():
    """Получение статистики активности пользователей"""
    now = timezone.now()
    periods = {
        'today': now - timedelta(days=1),
        'week': now - timedelta(weeks=1),
        'month': now - timedelta(days=30),
    }
    
    stats = {}
    for period_name, period_start in periods.items():
        stats[period_name] = {
            'posts': Post.objects.filter(created_at__gte=period_start).count(),
            'comments': Comment.objects.filter(created_date__gte=period_start).count(),
            'users': User.objects.filter(date_joined__gte=period_start).count(),
            'views': PostView.objects.filter(timestamp__gte=period_start).count(),
        }
    return stats

def get_popular_categories():
    """Получение популярных категорий с метриками"""
    return Category.objects.annotate(
        posts_count=Count('posts'),
        total_views=Sum('posts__views_count'),
        comments_count=Count('posts__comments'),
    ).order_by('-posts_count')[:5]

def get_total_media_size():
    """Получение общего размера медиа файлов"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_database_size():
    """Получение размра базы данных"""
    try:
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            return os.path.getsize(db_path)
    except:
        pass
    return 0

def get_latest_backup_info():
    """Получение информации о последнем бэкапе"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    try:
        if os.path.exists(backup_dir):
            files = os.listdir(backup_dir)
            if files:
                latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
                return {
                    'name': latest_file,
                    'size': os.path.getsize(os.path.join(backup_dir, latest_file)),
                    'date': datetime.fromtimestamp(os.path.getctime(os.path.join(backup_dir, latest_file)))
                }
    except:
        pass
    return None

def get_system_info():
    """Получение информации о системе"""
    return {
        'total_storage': get_total_media_size(),
        'database_size': get_database_size(),
        'cache_status': cache.get_stats() if hasattr(cache, 'get_stats') else None,
        'latest_backup': get_latest_backup_info(),
    }

@staff_member_required
@require_POST
def clear_cache(request):
    try:
        cache.clear()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
@require_POST
def toggle_user_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})

@staff_member_required
def generate_backup(request):
    """Создание бэкапа баз данных"""
    try:
        # Создаем прямое подключение к PostgreSQL
        conn = psycopg2.connect(
            dbname='django_blog_7f9a',
            user='django_blog_7f9a_user',
            password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
            host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
            port='5432',
            sslmode='require'
        )
        
        cursor = conn.cursor()

        # Получаем список вех таблиц
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()

        # Создаем словарь для хранения данных
        backup_data = {}
        
        # Получаем данные из каждой таблицы
        for table in tables:
            table_name = table[0]
            
            # Получаем структуру таблицы
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s
            """, [table_name])
            columns = cursor.fetchall()
            
            # Получаем данные таблицы
            cursor.execute(f'SELECT * FROM "{table_name}"')
            rows = cursor.fetchall()
            
            # Сохраяем структуру и данные таблицы
            backup_data[table_name] = {
                'structure': [
                    {'name': col[0], 'type': col[1]} for col in columns
                ],
                'data': [
                    dict(zip([col[0] for col in columns], row)) 
                    for row in rows
                ]
            }

        cursor.close()
        conn.close()

        # Добавляем метаданные
        backup_data['_metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'database': 'django_blog_7f9a',
            'version': 'PostgreSQL',
            'tables_count': len(tables),
            'total_records': sum(len(table_data['data']) for table_data in backup_data.values() if isinstance(table_data, dict) and 'data' in table_data)
        }

        # Созаем JSON-фал
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response = HttpResponse(
            json.dumps(backup_data, indent=2, default=str),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename=db_backup_{timestamp}.json'
        
        return response

    except Exception as e:
        messages.error(request, f'Ошибка при создании бэкапа: {str(e)}')
        print(f"Backup error: {str(e)}")  # Для отладки
        return redirect('blog:admin_panel')

@staff_member_required
@require_POST
def reset_user_password(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        # Геерируем новый пароль
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        user.set_password(new_password)
        user.save()
        
        # Отравляем email с новым паролем
        send_mail(
            'Сброс пароля',
            f'Ваш новый пароль: {new_password}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )
        
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def contacts(request):
    # Проверяем статус страницы
    try:
        page_settings = PageSettings.objects.get(page_name='contacts')
        if not page_settings.is_active:
            return render(request, 'blog/page_disabled.html', {
                'message': page_settings.disabled_message
            })
    except PageSettings.DoesNotExist:
        pass  # Если настройки нет, страница считается ативной
        
    return render(request, 'blog/contacts.html')

def search(request):
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query),
            is_published=True
        ).order_by('-created_at')
    else:
        posts = Post.objects.none()
    
    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'blog/search.html', context)

def can_moderate(user):
    """Проеряет, може ли пользователь модерировать контент"""
    return user.is_authenticated and (
        user.profile.role in ['creator', 'moderator'] or 
        user.is_staff
    )

@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Проверям права на удаление
    if post.author == request.user or can_moderate(request.user):
        post.delete()
        messages.success(request, 'Пост успено удален')
        return redirect('blog:home')
    messages.error(request, 'У ва нет прав для удаления этого поста')
    return redirect('blog:post_detail', slug=post.slug)

@require_POST
def update_activity(request):
    if request.user.is_authenticated:
        request.user.profile.save()  # Обновит last_seen
    return JsonResponse({'status': 'ok'})

@require_POST
def set_offline(request):
    if request.user.is_authenticated:
        request.user.profile.last_seen = timezone.now() - timezone.timedelta(minutes=6)
        request.user.profile.save()
    return JsonResponse({'status': 'ok'})

@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            messages.success(request, 'Комментарий успешно добавлен')
        else:
            messages.error(request, 'Комментарий не можт быть пустым')
    return redirect('blog:post_detail', slug=slug)

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('blog:profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'blog/profile_form.html', {
        'form': form,
        'title': 'Редактирование профиля'
    })

@staff_member_required
@require_POST
def bulk_user_action(request):
    """Масовые действия с пользователями"""
    action = request.POST.get('action')
    user_ids = request.POST.getlist('user_ids')
    
    if not user_ids:
        return JsonResponse({'success': False, 'error': 'No users selected'})
    
    users = User.objects.filter(id__in=user_ids)
    
    if action == 'activate':
        users.update(is_active=True)
    elif action == 'deactivate':
        users.update(is_active=False)
    elif action == 'delete':
        users.delete()
    
    return JsonResponse({'success': True})

@staff_member_required
@require_POST
def bulk_post_action(request):
    """Мссовые действя с посами"""
    action = request.POST.get('action')
    post_ids = request.POST.getlist('post_ids')
    
    if not post_ids:
        return JsonResponse({'success': False, 'error': 'No posts selected'})
    
    posts = Post.objects.filter(id__in=post_ids)
    
    if action == 'publish':
        posts.update(is_published=True)
    elif action == 'unpublish':
        posts.update(is_published=False)
    elif action == 'delete':
        posts.delete()
    
    return JsonResponse({'success': True})

@staff_member_required
def generate_report(request):
    """Генерация отчета о состоянии сайта"""
    report_data = {
        'user_stats': get_user_activity_stats(),
        'content_stats': {
            'posts': Post.objects.count(),
            'comments': Comment.objects.count(),
            'categories': Category.objects.count(),
            'tags': Tag.objects.count(),
        },
        'engagement_stats': {
            'total_views': Post.objects.aggregate(total_views=Sum('views_count'))['total_views'] or 0,
            'avg_comments_per_post': Comment.objects.count() / max(Post.objects.count(), 1),
            'active_users_ratio': User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count() / max(User.objects.count(), 1),
        },
        'popular_content': {
            'posts': Post.objects.order_by('-views_count')[:5],
            'categories': get_popular_categories(),
            'authors': User.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:5],
        }
    }
    
    # Создаем PDF отчет
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="site_report.pdf"'
    
    # Здесь ко для генерации PDF
    
    return response

@staff_member_required
@require_POST
def clean_database(request):
    """Очистк базы данных от неиспользуемых данных"""
    try:
        # Удаление неиспользуемых тего
        Tag.objects.filter(posts__isnull=True).delete()
        
        # Удаление старых просмотров
        old_views = timezone.now() - timedelta(days=90)
        PostView.objects.filter(timestamp__lt=old_views).delete()
        
        # Очистка кэша
        cache.clear()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def backup_database():
    """Создание резервнй копии бзы данных"""
    try:
        # Получаем путь к диектории для бэкапов из settings
        backup_dir = getattr(settings, 'BACKUP_DIR', None)
        if not backup_dir:
            # Если уь не здан в settings, создаем директорию backups в коне проекта
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')

        # Создаем директию для экапов, если она не существует
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Генерируем имя файла бэкапа с текущей датой и временем
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_path = settings.DATABASES['default']['NAME']
        backup_path = os.path.join(backup_dir, f'db_backup_{timestamp}.sqlite3')

        # Копируем файл базы данных
        shutil.copy2(db_path, backup_path)

        # Оставляем олько 5 последних бэкапов
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('db_backup_')])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(os.path.join(backup_dir, old_backup))

        print(f"Бэкап спешно создан: {backup_path}")
        return True
    except Exception as e:
        print(f"Ошибка при создании бкапа: {str(e)}")
        return False

def post_list(request):
    """Представление для списка всех постов"""
    # Получаем все публикованные посты
    posts_list = Post.objects.filter(is_published=True).order_by('-created_at')
    
    # Создаем объект пагинатора, 5 постов на страниц
    paginator = Paginator(posts_list, 5)  # Изменили с 12 на 5 постов
    
    # Получаем номер теущей страницы из GET-параметра
    page = request.GET.get('page')
    
    try:
        # Получаем объекты для текущей страницы
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если page не является целым числом, возвращаем первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если page больше максимального значени, возвращаем последнюю страницу
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'title': 'Все публикации',
    }
    return render(request, 'blog/post_list.html', context)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Содание нового оста'
        context['button_text'] = 'Опубликовать'
        context['is_edit'] = False
        return context
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = slugify(form.cleaned_data['title'])
        response = super().form_valid(form)
        messages.success(self.request, 'Пост успешно создан!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'slug': self.object.slug})

@staff_member_required
def toggle_page_status(request, page_name):
    """Включение/выключение страницы"""
    if request.method == 'POST':
        try:
            page_settings, created = PageSettings.objects.get_or_create(
                page_name=page_name,
                defaults={'updated_by': request.user}
            )
            page_settings.is_active = not page_settings.is_active
            page_settings.updated_by = request.user
            page_settings.save()
            
            status = 'активирована' if page_settings.is_active else 'деактивирована'
            messages.success(request, f'Страница {page_name} успешно {status}')
        except Exception as e:
            messages.error(request, f'Ошибка при изменении статуса страницы: {str(e)}')
    
    return redirect('blog:admin_panel')

@login_required
@require_POST
def update_profile_avatar(request):
    """Обновление аватара профиля"""
    if 'avatar' in request.FILES:
        try:
            profile = request.user.profile
            avatar_file = request.FILES['avatar']
            
            # Создаем директорию сли её нет
            avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            
            # Удаляем тарый аватар, если он есь
            if profile.avatar:
                old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(profile.avatar))
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            
            # Генерируем новое имя файла
            file_ext = os.path.splitext(avatar_file.name)[1]
            new_filename = f"avatar_{request.user.id}_{int(time.time())}{file_ext}"
            file_path = os.path.join('avatars', new_filename)
            
            # Сохраняем файл
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            with open(full_path, 'wb+') as destination:
                for chunk in avatar_file.chunks():
                    destination.write(chunk)
            
            # Обновляем профиль
            profile.avatar = file_path
            profile.save()
            
            return JsonResponse({
                'success': True,
                'avatar_url': os.path.join(settings.MEDIA_URL, file_path),
                'message': 'Аватар успешно обновлен'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'success': False,
        'error': 'Файл не был загружен'
    }, status=400)

@login_required
@require_POST
def update_profile_cover(request):
    """Обновление обложки профиля"""
    if 'cover' in request.FILES:
        try:
            profile = request.user.profile
            cover_file = request.FILES['cover']
            
            # Создаем директорию если её не
            cover_dir = os.path.join(settings.MEDIA_ROOT, 'covers')
            os.makedirs(cover_dir, exist_ok=True)
            
            # Удаляем сарую обложку, если она есть
            if profile.cover:
                old_cover_path = os.path.join(settings.MEDIA_ROOT, str(profile.cover))
                if os.path.exists(old_cover_path):
                    os.remove(old_cover_path)
            
            # Герируем новое имя файла
            file_ext = os.path.splitext(cover_file.name)[1]
            new_filename = f"cover_{request.user.id}_{int(time.time())}{file_ext}"
            file_path = os.path.join('covers', new_filename)
            
            # Сохраняем файл
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            with open(full_path, 'wb+') as destination:
                for chunk in cover_file.chunks():
                    destination.write(chunk)
            
            # Обновляем профиль
            profile.cover = file_path
            profile.save()
            
            return JsonResponse({
                'success': True,
                'cover_url': os.path.join(settings.MEDIA_URL, file_path),
                'message': 'Обложка успешно обновлена'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'success': False,
        'error': 'Файл не был загружен'
    }, status=400)

@login_required
@require_POST
def remove_profile_cover(request):
    """Удалние обложки профиля"""
    try:
        profile = request.user.profile
        if profile.cover:
            profile.cover.delete()
            profile.save()
            messages.success(request, 'Обложка профиля удалена')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, f'Ошибк при удалении бложки: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
def create_custom_invite(request):
    if request.method == 'POST':
        custom_code = request.POST.get('custom_code', '').strip().upper()
        if custom_code and len(custom_code) >= 3 and len(custom_code) <= 16:
            try:
                # Проверяем, не существует ли уже такой код
                if InviteCode.objects.filter(code=custom_code).exists():
                    messages.error(request, 'Такой код уже сущестует')
                else:
                    InviteCode.objects.create(
                        code=custom_code,
                        created_by=request.user
                    )
                    messages.success(request, f'Создан инвайт-код: {custom_code}')
            except Exception as e:
                messages.error(request, f'Ошибка при ��оздании кода: {str(e)}')
        else:
            messages.error(request, 'Недопустимый формат кода')
    return redirect('blog:admin_panel')

@staff_member_required
def deactivate_invite(request, code):
    if request.method == 'POST':
        try:
            invite = InviteCode.objects.get(code=code, is_active=True)
            invite.is_active = False
            invite.save()
            messages.success(request, f'Инвайт-код {code} деактивирован')
        except InviteCode.DoesNotExist:
            messages.error(request, 'Инвайт-код не найден')
    return redirect('blog:admin_panel')

@staff_member_required
def restore_database(request):
    """Восстановление базы данных из бэкапа"""
    if request.method == 'POST':
        try:
            backup_file = request.FILES['backup_file']
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in backup_file.chunks():
                    tmp_file.write(chunk)
            
            # Восстанавливае данные
            management.call_command('loaddata', tmp_file.name)
            
            # Удаляем временный файл
            os.unlink(tmp_file.name)
            
            messages.success(request, 'База данных успешно восстановлена')
        except Exception as e:
            messages.error(request, f'Ошибка при восстановлении: {str(e)}')
        
        return redirect('blog:admin_panel')
    
    return render(request, 'blog/restore_database.html')

def health_check(request):
    """Проверка здоровья приложения"""
    try:
        # Проверяем подключение к базе данных
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
        # Проверяем наличие данных
        users_count = User.objects.count()
        posts_count = Post.objects.count()
        
        status = {
            'status': 'healthy',
            'database': 'connected',
            'users_count': users_count,
            'posts_count': posts_count
        }
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

@staff_member_required
def clear_database(request):
    if request.method == 'POST':
        try:
            management.call_command('clear_database')
            messages.success(request, 'База данных успешно очищена')
        except Exception as e:
            messages.error(request, f'Ошибка при очистке базы данных: {str(e)}')
    return redirect('blog:admin_panel')
