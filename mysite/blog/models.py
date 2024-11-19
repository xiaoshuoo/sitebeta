from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class Profile(models.Model):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('creator', 'Создатель'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    @property
    def is_online(self):
        return timezone.now() - self.last_seen < timezone.timedelta(minutes=5)

    def get_role_display_with_icon(self):
        icons = {
            'user': 'fa-user',
            'creator': 'fa-crown',
            'moderator': 'fa-shield-alt'
        }
        return {
            'name': self.get_role_display(),
            'icon': icons.get(self.role, 'fa-user')
        }

    def get_last_seen(self):
        if self.is_online:
            return 'Онлайн'
        
        now = timezone.now()
        diff = now - self.last_seen
        
        if diff.days > 0:
            return f'Был(а) {diff.days} дн. назад'
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f'Был(а) {hours} ч. назад'
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f'Был(а) {minutes} мин. назад'
        else:
            return f'Был(а) только что'

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Создаем директории для файлов если их нет
        if not os.path.exists('media/avatars'):
            os.makedirs('media/avatars')
        if not os.path.exists('media/covers'):
            os.makedirs('media/covers')
            
        # Сохраняем файлы
        if self.avatar:
            self.avatar.save(
                self.avatar.name,
                self.avatar.file,
                save=False
            )
        if self.cover:
            self.cover.save(
                self.cover.name,
                self.cover.file,
                save=False
            )
            
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файлы при удалении профиля
        if self.avatar:
            if os.path.isfile(self.avatar.path):
                os.remove(self.avatar.path)
        if self.cover:
            if os.path.isfile(self.cover.path):
                os.remove(self.cover.path)
        super().delete(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль пользователя при создании пользователя"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль пользователя при сохранении пользователя"""
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, default='fa-folder')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    _posts_count = models.IntegerField(default=0, db_column='posts_count')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = 'category'
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        
        # Сначала сохраняем объект
        super().save(*args, **kwargs)
        
        # Теперь можно обновить количество постов
        if self.pk:  # Проверяем, что объект уже сохранен
            self._posts_count = self.posts.count()
            super().save(update_fields=['_posts_count'])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    @property
    def posts_count(self):
        return self._posts_count

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'post'
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f'Комментарий от {self.author} к {self.post}'

class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['post', 'user'],  # Для авторизованных пользователей
            ['post', 'session_key'],  # Для анонимных пользователей
        ]

    def __str__(self):
        return f"{self.post.title} - {self.user.username if self.user else 'Anonymous'}"

class InviteCode(models.Model):
    code = models.CharField(max_length=8, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invites')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_invites')
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invite {self.code}"

    def use(self, user):
        if self.is_active and not self.used_by:
            self.used_by = user
            self.is_active = False
            self.used_at = timezone.now()
            self.save()

class PageSettings(models.Model):
    page_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    disabled_message = models.TextField(default='Страница временно недоступна')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Добавляем константы для имен страниц
    CONTACTS_PAGE = 'contacts'
    CREATE_POST_PAGE = 'create_post'
    
    PAGE_CHOICES = [
        (CONTACTS_PAGE, 'Страница контактов'),
        (CREATE_POST_PAGE, 'Создание постов'),
    ]
    
    page_name = models.CharField(
        max_length=100,
        unique=True,
        choices=PAGE_CHOICES
    )

    class Meta:
        verbose_name = 'Настройка страницы'
        verbose_name_plural = 'Настройки страниц'

    def __str__(self):
        return f"{self.get_page_name_display()} ({'Активна' if self.is_active else 'Отключена'})"