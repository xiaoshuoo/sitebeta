from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Count, Sum, Max, F, Q
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Post, Category, Tag, InviteCode, Profile, 
    Comment, PostView, PageSettings
)
from .forms import PostForm, CustomUserCreationForm, ProfileUpdateForm
from django.utils.text import slugify
import random
import string
from django.contrib.admin.models import LogEntry
from datetime import timedelta
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from django.conf import settings
from datetime import datetime
import json
import shutil
from datetime import datetime
import zipfile
from django.db import connection
from django.apps import apps

def home(request):
    """Представление главной страницы"""
    context = {
        'posts': Post.objects.filter(
            is_published=True
        ).select_related(
            'author', 'category', 'author__profile'
        ).prefetch_related(
            'tags'
        ).order_by('-created_at'),
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

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация успешно завершена! Теперь вы можете войти.')
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Ошибка в поле {field}: {error}')
        return super().form_invalid(form)

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
                return redirect('blog:home')  # Перенаправляем на главную
                
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
    form_class = ProfileUpdateForm
    template_name = 'blog/profile_form.html'
    success_url = reverse_lazy('blog:profile')

    def get_object(self, queryset=None):
        # Получаем или создаем профиль для текущего пользователя
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        profile = form.save(commit=False)
        
        # Обработка аватара
        if 'avatar' in self.request.FILES:
            if profile.avatar:
                try:
                    profile.avatar.delete(save=False)
                except:
                    pass
            profile.avatar = self.request.FILES['avatar']
        
        # Обработка обложки
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
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

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
                # С��здаем новое подключение для сохранения
                with transaction.atomic():
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

    # Получаем категории отдельным запросом
    categories = Category.objects.only('id', 'name').order_by('name')
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Создать пост',
        'button_text': 'Опубликовать',
        'categories': categories,
    })

def post_detail(request, slug):
    """Детальное представление поста"""
    # Получаем пост или возвращаем 404
    post = get_object_or_404(Post.objects.select_related('author', 'category'), slug=slug)
    
    # Увеличиваем счетчик просмотров только для уникальных пользователей
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
            # Если просмотра нет, создаем новый
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
        is_published=True
    ).exclude(
        id=post.id
    ).only(
        'title', 'slug', 'created_at', 'views_count',
        'author__username',
        'category__name'
    ).select_related(
        'author', 'category'
    )[:3]
    
    context = {
        'post': post,
        'similar_posts': similar_posts,
    }
    return render(request, 'blog/post_detail.html', context)

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
        initial_data = {
            'content': post.content,
        }
        form = PostForm(instance=post, initial=initial_data)
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'post': post,
        'title': 'Редактировать пост',
        'button_text': 'Сохранить изменения',
        'is_edit': True
    })

def categories_list(request):
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
def my_posts(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
    context = {
        'posts': user_posts,
        'title': 'Мои посты'
    }
    return render(request, 'blog/my_posts.html', context)

def user_profile(request, username):
    viewed_user = get_object_or_404(User, username=username)
    
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
    
    streak_days = calculate_streak_days(viewed_user)
    achievements_count = calculate_achievements(viewed_user)
    
    context = {
        'viewed_user': viewed_user,
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

def contacts(request):
    try:
        page_settings = PageSettings.objects.get(page_name='contacts')
        if not page_settings.is_active:
            return render(request, 'blog/page_disabled.html', {
                'message': page_settings.disabled_message
            })
    except PageSettings.DoesNotExist:
        pass
        
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

def calculate_streak_days(user):
    """Подсчет дней подяд с публкацими"""
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
            
        # Если разница между постами больше 1 дня, прерываем подсчет
        if (last_post_date - post_date).days > 1:
            break
            
        streak += 1
        last_post_date = post_date
        
    return streak

def calculate_achievements(user):
    """Подсчет достижений пользователя"""
    achievements = 0
    
    # Достижение за первый пост
    if Post.objects.filter(author=user, is_published=True).exists():
        achievements += 1
    
    # Достижение за 10 постов
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

def generate_invite_code():
    """Генерация 8-символьного кода приглашения"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@login_required
def create_invite(request):
    if not request.user.is_staff:
        messages.error(request, "У вас нет прав для создания приглашений")
        return redirect('blog:home')
    
    code = generate_invite_code()
    InviteCode.objects.create(code=code, created_by=request.user)
    messages.success(request, f"Создан код приглашения: {code}")
    return redirect('blog:invite_codes')

@login_required
def invite_codes(request):
    codes = InviteCode.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'blog/invite_codes.html', {'codes': codes})

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
    
    # Добавляем получение настроек страниц
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
        
        # Статистика активности
        'new_users_month': User.objects.filter(date_joined__gte=thirty_days_ago).count(),
        'new_posts_month': Post.objects.filter(created_at__gte=thirty_days_ago).count(),
        'active_users_month': User.objects.filter(last_login__gte=thirty_days_ago).count(),
        'total_views': Post.objects.aggregate(total_views=Sum('views_count'))['total_views'] or 0,
        
        # Списки для управления
        'users': User.objects.all().order_by('-date_joined')[:10],
        'recent_posts': Post.objects.select_related('author', 'category').order_by('-created_at')[:10],
        'recent_comments': Comment.objects.select_related('author', 'post').order_by('-created_date')[:10],
        'active_invites': active_invites,
        'popular_categories': popular_categories,
        
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

def get_database_info():
    """Получение базовой информации о базе данных"""
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

        # Получаем версию PostgreSQL
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]

        # Сначала получаем список существующих таблиц
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        existing_tables = [table[0] for table in cursor.fetchall()]

        # Получаем статистику записей
        stats = {
            'users': 0,
            'posts': 0,
            'comments': 0,
            'profiles': 0,
            'categories': 0
        }

        # Подсчитываем записи только для существующих таблиц
        if 'auth_user' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            stats['users'] = cursor.fetchone()[0]

        if 'blog_post' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM blog_post")
            stats['posts'] = cursor.fetchone()[0]

        if 'blog_comment' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM blog_comment")
            stats['comments'] = cursor.fetchone()[0]

        if 'blog_profile' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM blog_profile")
            stats['profiles'] = cursor.fetchone()[0]

        if 'blog_category' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM blog_category")
            stats['categories'] = cursor.fetchone()[0]

        # Получаем информацию о таблицах
        tables_info = []
        for table_name in existing_tables:
            cursor.execute(f"""
                SELECT 
                    pg_size_pretty(pg_total_relation_size(quote_ident(%s))),
                    pg_total_relation_size(quote_ident(%s)),
                    (SELECT count(*) FROM information_schema.columns WHERE table_name = %s)
                """, [table_name, table_name, table_name])
            
            table_info = cursor.fetchone()
            tables_info.append({
                'name': table_name,
                'size': table_info[0],
                'raw_size': table_info[1],
                'columns': table_info[2]
            })

        # Получаем ощий размер базы данных
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        total_size = cursor.fetchone()[0]

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

        cursor.close()
        conn.close()

        return {
            'connection_status': {
                'is_connected': True,
                'version': version,
            },
            'size': total_size,
            'tables': tables_info,
            'stats': stats,
            'memory_usage': {
                'total_connections': connections[0] if connections else 0,
                'active_connections': connections[1] if connections else 0,
                'idle_connections': connections[2] if connections else 0,
                'total_size': total_size,
                'table_count': len(existing_tables),
                'total_rows': sum(stats.values())
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
                'total_size': 'N/A',
                'table_count': 0,
                'total_rows': 0
            }
        }

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

def get_total_media_size():
    """Получение общего размера медиа файлов"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_database_size():
    """Получение размера базы данных"""
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

@staff_member_required
@require_POST
def toggle_user_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f'Пользователь {"активирован" if user.is_active else "деактивирован"}'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Пользователь не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_POST
def update_activity(request):
    """Обновление времени последней активности пользователя"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            profile.last_seen = timezone.now()
            profile.save(update_fields=['last_seen'])
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)

@require_POST
def set_offline(request):
    """Установка статуса оффлайн для пользователя"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            profile.last_seen = timezone.now() - timezone.timedelta(minutes=6)
            profile.save(update_fields=['last_seen'])
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)

@login_required
@require_POST
def add_comment(request, slug):
    """Добавление комментария к посту"""
    post = get_object_or_404(Post, slug=slug)
    
    try:
        content = request.POST.get('content', '').strip()
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_date': comment.created_date.strftime('%d.%m.%Y %H:%M'),
                    'author_avatar': comment.author.profile.avatar.url if comment.author.profile.avatar else None,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Комментарий не может быть пустым'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@staff_member_required
def generate_backup(request):
    """Создание резервной копии данных"""
    try:
        # Создаем директорию для бэкапов, если её нет
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Генерируем имя файла бэкапа
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.zip'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Создаем ZIP-архив
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # Бэкап медиафайлов
            if os.path.exists(settings.MEDIA_ROOT):
                for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, settings.BASE_DIR)
                        backup_zip.write(file_path, arc_name)
            
            # Бэкап данных из базы
            data = {
                'users': list(User.objects.values()),
                'profiles': list(Profile.objects.values()),
                'categories': list(Category.objects.values()),
                'tags': list(Tag.objects.values()),
                'posts': list(Post.objects.values()),
                'comments': list(Comment.objects.values()),
                'page_settings': list(PageSettings.objects.values()),
                'invite_codes': list(InviteCode.objects.values()),
            }
            
            # Записываем данные в JSON-файл внутри архива
            backup_zip.writestr('data.json', json.dumps(data, indent=2, default=str))
        
        # Формируем URL для скачивания
        backup_url = os.path.join(settings.MEDIA_URL, 'backups', backup_filename)
        
        messages.success(request, f'Резервная копия успешно создана: {backup_filename}')
        return JsonResponse({
            'success': True,
            'backup_url': backup_url,
            'filename': backup_filename,
            'size': os.path.getsize(backup_path)
        })
        
    except Exception as e:
        messages.error(request, f'Ошибка при создании резервной копии: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@staff_member_required
def reset_user_password(request, user_id):
    """Сброс пароля пользователя администратором"""
    try:
        user = User.objects.get(id=user_id)
        # Генерируем новый пароль
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        user.set_password(new_password)
        user.save()
        
        messages.success(request, f'Пароль пользователя {user.username} успешно сброшен. Новый пароль: {new_password}')
        return JsonResponse({
            'success': True,
            'message': f'Новый пароль: {new_password}'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Пользователь не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@staff_member_required
def bulk_user_action(request):
    """Массовые действия с пользователями"""
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            user_ids = request.POST.getlist('user_ids[]')
            users = User.objects.filter(id__in=user_ids)
            
            if action == 'activate':
                users.update(is_active=True)
                message = 'Пользователи активированы'
            elif action == 'deactivate':
                users.update(is_active=False)
                message = 'Пользователи деактивированы'
            elif action == 'delete':
                users.delete()
                message = 'Пользователи удалены'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Неизвестное действие'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'message': message
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return JsonResponse({
        'success': False,
        'error': 'Метод не поддерживается'
    }, status=405)

@staff_member_required
def bulk_post_action(request):
    """Массовые действия с постами"""
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            post_ids = request.POST.getlist('post_ids[]')
            posts = Post.objects.filter(id__in=post_ids)
            
            if action == 'publish':
                posts.update(is_published=True)
                message = 'Посты опубликованы'
            elif action == 'unpublish':
                posts.update(is_published=False)
                message = 'Посты сняты с публикации'
            elif action == 'delete':
                posts.delete()
                message = 'Посты удалены'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Неизвестное действие'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'message': message
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return JsonResponse({
        'success': False,
        'error': 'Метод не поддерживается'
    }, status=405)

@staff_member_required
def generate_report(request):
    """Генерация отчета о состоянии сайта"""
    try:
        report_data = {
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'staff': User.objects.filter(is_staff=True).count(),
                'new_this_month': User.objects.filter(
                    date_joined__gte=timezone.now() - timedelta(days=30)
                ).count()
            },
            'posts': {
                'total': Post.objects.count(),
                'published': Post.objects.filter(is_published=True).count(),
                'draft': Post.objects.filter(is_published=False).count(),
                'total_views': Post.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
            },
            'categories': {
                'total': Category.objects.count(),
                'most_popular': list(Category.objects.annotate(
                    posts_count=Count('posts')
                ).order_by('-posts_count').values('name', 'posts_count')[:5])
            },
            'comments': {
                'total': Comment.objects.count(),
                'this_month': Comment.objects.filter(
                    created_date__gte=timezone.now() - timedelta(days=30)
                ).count()
            },
            'system': get_system_info(),
            'database': get_database_info()
        }
        
        return JsonResponse({
            'success': True,
            'report': report_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@staff_member_required
def clean_database(request):
    """Очистка базы данных от неиспользуемых данных"""
    try:
        # Удаляем неиспользуемые теги
        unused_tags = Tag.objects.annotate(
            posts_count=Count('posts')
        ).filter(posts_count=0)
        deleted_tags = unused_tags.count()
        unused_tags.delete()
        
        # Удаляем старые просмотры
        old_views = PostView.objects.filter(
            timestamp__lt=timezone.now() - timedelta(days=90)
        )
        deleted_views = old_views.count()
        old_views.delete()
        
        # Очищаем кэш
        cache.clear()
        
        return JsonResponse({
            'success': True,
            'message': f'Удалено {deleted_tags} тегов и {deleted_views} старых просмотров'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@staff_member_required
def restore_database(request):
    """Восстановление базы данных из резервной копии"""
    if request.method == 'POST' and request.FILES.get('backup_file'):
        try:
            backup_file = request.FILES['backup_file']
            
            # Создаем временную директорию для распаковки
            temp_dir = os.path.join(settings.BASE_DIR, 'temp_restore')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Распаковываем архив
            with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Загружаем данные из JSON
            with open(os.path.join(temp_dir, 'data.json'), 'r') as f:
                data = json.load(f)
            
            # Восстанавливаем данные
            with transaction.atomic():
                # Очищаем существующие данные
                Post.objects.all().delete()
                Category.objects.all().delete()
                Tag.objects.all().delete()
                Comment.objects.all().delete()
                
                # Восстанавливаем данные
                for model_name, items in data.items():
                    model = apps.get_model('blog', model_name)
                    for item in items:
                        model.objects.create(**item)
            
            # Очищаем временную директорию
            shutil.rmtree(temp_dir)
            
            messages.success(request, 'База данных успешно восстановлена')
            return JsonResponse({'success': True})
            
        except Exception as e:
            messages.error(request, f'Ошибка при восстановлении: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'success': False,
        'error': 'Файл резервной копии не предоставлен'
    }, status=400)

@staff_member_required
def toggle_page_status(request, page_name):
    """Включение/выключение страницы"""
    try:
        page_settings = PageSettings.objects.get(page_name=page_name)
        page_settings.is_active = not page_settings.is_active
        page_settings.updated_by = request.user
        page_settings.save()
        
        return JsonResponse({
            'success': True,
            'is_active': page_settings.is_active
        })
    except PageSettings.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Настройки страницы не найдены'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def update_profile_cover(request):
    """Обновление обложки профиля"""
    if request.method == 'POST' and request.FILES.get('cover'):
        try:
            profile = request.user.profile
            if profile.cover:
                profile.cover.delete(save=False)
            profile.cover = request.FILES['cover']
            profile.save()
            
            return JsonResponse({
                'success': True,
                'cover_url': profile.cover.url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return JsonResponse({
        'success': False,
        'error': 'Файл обложки не предоставлен'
    }, status=400)

@login_required
def update_profile_avatar(request):
    """Обновление аватара профиля"""
    if request.method == 'POST' and request.FILES.get('avatar'):
        try:
            profile = request.user.profile
            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar = request.FILES['avatar']
            profile.save()
            
            return JsonResponse({
                'success': True,
                'avatar_url': profile.avatar.url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return JsonResponse({
        'success': False,
        'error': 'Файл аватара не предоставлен'
    }, status=400)

@login_required
def remove_profile_cover(request):
    """Удаление обложки профиля"""
    try:
        profile = request.user.profile
        if profile.cover:
            profile.cover.delete()
            profile.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@staff_member_required
def create_custom_invite(request):
    """Создание пользовательского инвайт-кода"""
    if request.method == 'POST':
        try:
            code = request.POST.get('code', '').strip().upper()
            if not code:
                code = generate_invite_code()
            elif InviteCode.objects.filter(code=code).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Такой код уже существует'
                }, status=400)
            
            invite = InviteCode.objects.create(
                code=code,
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'code': invite.code
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return JsonResponse({
        'success': False,
        'error': 'Метод не поддерживается'
    }, status=405)

@staff_member_required
def deactivate_invite(request, code):
    """Деактивация инвайт-кода"""
    try:
        invite = InviteCode.objects.get(code=code)
        invite.is_active = False
        invite.save()
        return JsonResponse({'success': True})
    except InviteCode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Инвайт-код не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def health_check(request):
    """Проверка состояния системы"""
    try:
        # Проверяем подключение к базе данных
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Проверяем работу кэша
        cache_key = 'health_check'
        cache.set(cache_key, 'ok', 10)
        cache_status = cache.get(cache_key) == 'ok'
        
        # Проверяем доступ к медиа-директории
        media_writable = os.access(settings.MEDIA_ROOT, os.W_OK)
        
        status = {
            'database': True,
            'cache': cache_status,
            'media_storage': media_writable,
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)

def clear_database(request):
    """Очистка базы данных"""
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Недостаточно прав'
        }, status=403)
        
    try:
        # Очищаем таблицы
        Post.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Comment.objects.all().delete()
        PostView.objects.all().delete()
        
        # Очищаем кэш
        cache.clear()
        
        return JsonResponse({
            'success': True,
            'message': 'База данных успешно очищена'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def post_list(request):
    """Список всех опубликованных постов"""
    posts = Post.objects.filter(
        is_published=True
    ).select_related(
        'author', 
        'category',
        'author__profile'
    ).prefetch_related(
        'tags'
    ).order_by('-created_at')
    
    # Фильтрация по категории
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Фильтрация по тегу
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Фильтрация по автору
    author_username = request.GET.get('author')
    if author_username:
        posts = posts.filter(author__username=author_username)
    
    # Поиск по заголовку и содержимому
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    # Сортировка
    sort_by = request.GET.get('sort', '-created_at')
    valid_sort_fields = {
        'created_at': 'created_at',
        '-created_at': '-created_at',
        'views': '-views_count',
        'title': 'title',
        '-title': '-title'
    }
    if sort_by in valid_sort_fields:
        posts = posts.order_by(valid_sort_fields[sort_by])
    
    context = {
        'posts': posts,
        'categories': Category.objects.all(),
        'popular_tags': Tag.objects.annotate(
            posts_count=Count('posts')
        ).order_by('-posts_count')[:10],
        'query': query,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'current_author': author_username,
        'current_sort': sort_by
    }
    return render(request, 'blog/post_list.html', context)
