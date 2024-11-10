from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
import random
import string
from .models import Post, Category, Tag, InviteCode, UserProfile
from .forms import PostForm, CustomUserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.http import require_POST

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Получаем данные из формы
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            category = form.cleaned_data['category']
            is_published = form.cleaned_data.get('is_published', False)
            thumbnail = request.FILES.get('thumbnail')
            
            # Заполняем поля поста
            post.title = title
            post.content = content
            post.category = category
            post.is_published = is_published
            if thumbnail:
                post.thumbnail = thumbnail
            
            # Сохраняем пост
            post.save()
            
            messages.success(request, 'Пост успешно создан!')
            return redirect('blog:post_detail', pk=post.pk)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            print(form.errors)  # Для отладки
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Создать пост',
        'button_text': 'Опубликовать'
    })

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            # Обработка Markdown контента
            content = form.cleaned_data['content']
            post.content = content
            
            # Сохраняем пост
            post.save()
            
            # Если есть теги, обновляем их
            if form.cleaned_data.get('tags'):
                post.tags.set(form.cleaned_data['tags'])
            
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('blog:post_detail', pk=post.pk)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'post': post,
        'title': 'Редактировать пост',
        'button_text': 'Сохранить изменения'
    })

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Увеличиваем счетчик просмотров
    post.increment_views(request.user)
    
    # Получаем похожие посты
    similar_posts = Post.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id).order_by('-views_count')[:3]
    
    context = {
        'post': post,
        'similar_posts': similar_posts,
    }
    return render(request, 'blog/post_detail.html', context)

def home(request):
    # Создаем категорию по умолчанию, если её нет
    default_category, created = Category.objects.get_or_create(
        id=1,
        defaults={
            'name': 'Общее',
            'slug': 'general',
            'icon': 'fa-folder',
            'description': 'Общая категория'
        }
    )
    
    # Фильтруем посты, чтобы показывать только те, у которых есть категория с валидным slug
    posts = Post.objects.filter(
        is_published=True,
        category__isnull=False,
        category__slug__isnull=False
    ).exclude(category__slug='').order_by('-created_at')
    
    # Фильтруем категории, исключая те, у которых нет slug
    categories = Category.objects.exclude(slug__isnull=True).exclude(slug='')
    
    # Получаем теги
    tags = Tag.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'blog/home.html', context)

def categories_list(request):
    # Фильтруем категории, исключая те, у которых нет slug
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
    user_profile = request.user.profile  # Получаем профиль текущего пользователя
    user_posts = Post.objects.filter(author=request.user, is_published=True).order_by('-created_at')
    
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'posts_count': user_posts.count(),
        'user_posts': user_posts,
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
    codes = InviteCode.objects.filter(created_by=request.user)
    return render(request, 'blog/invite_codes.html', {'codes': codes})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Создаем пользователя, но не сохраняем в базу
            user = form.save(commit=False)
            user.save()  # Теперь сохраняем пользователя
            
            # Получаем код приглашения из формы
            invite_code = form.cleaned_data.get('invite_code')
            
            # Помечаем код как использованный
            invite_code.used_by = user
            invite_code.is_active = False
            invite_code.save()
            
            # Профиль пользователя создастся автоматически через сигнал
            
            # Входим в систему
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('blog:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'blog/profile_edit.html'
    fields = ['avatar', 'bio', 'website', 'location']
    success_url = reverse_lazy('blog:profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user, is_published=True).order_by('-created_at')
    
    context = {
        'profile_user': user,
        'user_posts': user_posts,
        'posts_count': user_posts.count(),
    }
    return render(request, 'blog/user_profile.html', context)

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален!')
        return redirect('blog:home')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@staff_member_required
def admin_panel(request):
    context = {
        'users_count': User.objects.count(),
        'posts_count': Post.objects.count(),
        'categories_count': Category.objects.count(),
        'active_invites': InviteCode.objects.filter(is_active=True).count(),
        'users': User.objects.all().order_by('-date_joined'),
        'recent_logs': [], # Здесь можно добавить логирование действий
    }
    return render(request, 'blog/admin_panel.html', context)

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
  