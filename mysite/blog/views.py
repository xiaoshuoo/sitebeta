from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, Category, InviteCode, UserProfile, Tag, PostAttachment
from .forms import PostForm, CustomUserCreationForm, UserProfileForm
import random
import string
from django.views.decorators.csrf import csrf_protect

@csrf_protect
@login_required
def create_post(request):
    # Проверяем доступ к разделу
    if not request.user.is_staff:  # Только для администраторов
        messages.error(request, 'У вас нет доступа к этому разделу')
        return redirect('blog:home')
        
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Автоматическая публикация, если выбрана опция
            if request.POST.get('publish_now') == 'on':
                post.is_published = True
            
            post.save()
            
            files = request.FILES.getlist('attachments[]')
            for file in files:
                attachment = PostAttachment.objects.create(file=file)
                post.attachments.add(attachment)
            
            messages.success(request, 'Пост успешно создан!')
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'can_publish': request.user.is_staff  # Передаем флаг возможности публикации
    })

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {'form': form, 'post': post})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def home(request):
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'blog/home.html', {
        'posts': posts,
        'categories': categories
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, 'blog/categories.html', {'categories': categories})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, is_published=True).order_by('-created_at')
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'posts': posts
    })

@login_required
def about(request):
    if not request.user.is_staff:  # Только для администраторов
        messages.error(request, 'У вас нет доступа к этому разделу')
        return redirect('blog:home')
        
    context = {
        'users_count': User.objects.count(),
        'posts_count': Post.objects.filter(is_published=True).count(),
        'categories_count': Category.objects.count(),
    }
    return render(request, 'blog/about.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Отправка email
        full_message = f"От: {name}\nEmail: {email}\n\n{message}"
        try:
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Ваше сообщение успешно отправлено!')
        except Exception as e:
            messages.error(request, 'Произошла ошибка при отправке сообщения.')
        
        return redirect('blog:contact')
    
    return render(request, 'blog/contact.html')

@login_required
def profile(request):
    # Получаем или создаем профиль пользователя
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    user_posts = Post.objects.filter(author=request.user)
    published_posts = user_posts.filter(is_published=True)
    draft_posts = user_posts.filter(is_published=False)
    
    # Получаем категории с количеством постов пользователя
    categories_with_counts = []
    for category in Category.objects.filter(posts__author=request.user).distinct():
        post_count = category.posts.filter(author=request.user).count()
        categories_with_counts.append({
            'category': category,
            'post_count': post_count
        })
    
    context = {
        'user_profile': user_profile,
        'total_posts': user_posts.count(),
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'recent_posts': published_posts.order_by('-created_at')[:5],
        'categories_with_counts': categories_with_counts
    }
    return render(request, 'blog/profile.html', context)

@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'blog/my_posts.html', {'posts': posts})

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
            user = form.save()
            invite = form.cleaned_data['invite_code']
            invite.used_by = user
            invite.is_active = False
            invite.save()
            
            # Профиль создастся автоматически через сигнал
            
            login(request, user)
            messages.success(request, "Регистрация успешно завершена!")
            return redirect('blog:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'blog/profile_edit.html'
    success_url = reverse_lazy('blog:profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.get_object()
        return context
  