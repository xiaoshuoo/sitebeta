from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import hashlib
import time
from django.conf import settings
from .cloudinary_storage import CustomCloudinaryStorage
import cloudinary
import logging
from cloudinary.models import CloudinaryField

logger = logging.getLogger(__name__)

def avatar_upload_path(instance, filename):
    """Генерация пути для аватара"""
    ext = filename.split('.')[-1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"
    # Возвращаем путь без media/
    return f"avatars/{new_filename}"

def cover_upload_path(instance, filename):
    """Генерация пути для обложки"""
    ext = filename.split('.')[-1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"
    # Возвращаем путь без media/
    return f"covers/{new_filename}"

def thumbnail_upload_path(instance, filename):
    """Генерация пути для миниатюры"""
    ext = filename.split('.')[-1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"
    # Возвращаем путь без media/
    return f"thumbnails/{new_filename}"

def story_cover_path(instance, filename):
    """Генерация пути для обложки истории"""
    ext = filename.split('.')[-1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"
    return f"stories/covers/{new_filename}"

class Title(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#8B5CF6')  # HEX color
    icon = models.CharField(max_length=50, default='fas fa-award')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Титул"
        verbose_name_plural = "Титулы"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('creator', 'Создатель')
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = CloudinaryField('avatar', 
        folder='avatars/',
        null=True, 
        blank=True,
        transformation={
            'width': 400, 
            'height': 400,
            'crop': 'fill',
            'gravity': 'face'
        }
    )
    cover = CloudinaryField('cover',
        folder='covers/',
        null=True,
        blank=True, 
        transformation={
            'width': 1500,
            'height': 500,
            'crop': 'fill',
            'gravity': 'center'
        }
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    titles = models.ManyToManyField('Title', blank=True)

    @property
    def is_online(self):
        return timezone.now() - self.last_seen < timezone.timedelta(minutes=5)

    def get_role_display_with_icon(self):
        role_icons = {
            'user': {'name': 'Пользователь', 'icon': 'fa-user'},
            'moderator': {'name': 'Модератор', 'icon': 'fa-shield-alt'},
            'creator': {'name': 'Создатель', 'icon': 'fa-crown'}
        }
        return role_icons.get(self.role, {'name': self.get_role_display(), 'icon': 'fa-user'})

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
        if self.avatar:
            # Для CloudinaryField используем public_id вместо name
            if hasattr(self.avatar, 'public_id'):
                if 'avatars/avatars/' in self.avatar.public_id:
                    self.avatar.public_id = self.avatar.public_id.replace('avatars/avatars/', 'avatars/')
        if self.cover:
            if hasattr(self.cover, 'public_id'):
                if 'covers/covers/' in self.cover.public_id:
                    self.cover.public_id = self.cover.public_id.replace('covers/covers/', 'covers/')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файлы из Cloudinary при удалении профиля
        if self.avatar:
            try:
                cloudinary.uploader.destroy(self.avatar.public_id)
            except Exception as e:
                logger.error(f"Error deleting avatar from Cloudinary: {str(e)}")
        if self.cover:
            try:
                cloudinary.uploader.destroy(self.cover.public_id)
            except Exception as e:
                logger.error(f"Error deleting cover from Cloudinary: {str(e)}")
        super().delete(*args, **kwargs)

    def get_cover_url(self):
        """Метод для получения URL обложки"""
        if self.cover:
            return self.cover
        return None

    def get_avatar_url(self):
        """Метод для получения URL аватарки"""
        if self.avatar:
            return self.avatar
        return None

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
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-folder')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posts_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def update_posts_count(self):
        """Обновляет количество постов в категории"""
        from django.db.models.signals import post_save
        from django.db import transaction
        
        with transaction.atomic():
            # Используем post_set вместо posts
            count = self.post_set.count()
            
            if self.posts_count != count:
                Category.objects.filter(id=self.id).update(
                    posts_count=count,
                    updated_at=timezone.now()
                )
                self.refresh_from_db()
    
    def save(self, *args, **kwargs):
        """Переопределяем метод save для автоматического обновления posts_count"""
        super().save(*args, **kwargs)
        self.update_posts_count()

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=False)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
            # Если slug пустой после slugify, генерируем уникальный
            if not self.slug:
                self.slug = f"tag-{uuid.uuid4().hex[:8]}"
            # Проверяем уникальность
            counter = 1
            original_slug = self.slug
            while Tag.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    thumbnail = CloudinaryField('thumbnail', 
        folder='thumbnails/',
        null=True, 
        blank=True,
        transformation={
            'width': 1200,
            'height': 630,
            'crop': 'fill',
            'gravity': 'center'
        }
    )
    is_published = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_published']),
            models.Index(fields=['author']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Создаем slug если его нет
        if not self.slug:
            self.slug = slugify(self.title)
            counter = 1
            temp_slug = self.slug
            while Post.objects.filter(slug=temp_slug).exists():
                temp_slug = f"{self.slug}-{counter}"
                counter += 1
            self.slug = temp_slug

        # Проверяем размер thumbnail если он есть
        if self.thumbnail and hasattr(self.thumbnail, 'file'):
            try:
                if self.thumbnail.size > 50 * 1024 * 1024:  # 50MB
                    raise ValueError('Размер изображения не должен превышать 50MB')
            except (AttributeError, FileNotFoundError):
                pass  # Игнорируем ошибки если файл недоступен

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def comments_count(self):
        return self.comment_set.count()

    def increment_views(self, user=None, session_key=None):
        # Увеличиваем счетчик просмотров
        self.views_count += 1
        self.save()

        # Записываем информацию о просмотре
        try:
            PostView.objects.get_or_create(
                post=self,
                user=user,
                session_key=session_key
            )
        except Exception as e:
            logger.error(f"Error creating post view: {str(e)}")

    def get_thumbnail_url(self):
        """Метод для получения URL миниатюры"""
        if self.thumbnail:
            try:
                return self.thumbnail.url
            except Exception as e:
                logger.error(f"Error getting thumbnail URL: {str(e)}")
                try:
                    return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{self.thumbnail.public_id}"
                except Exception as e:
                    logger.error(f"Error getting direct thumbnail URL: {str(e)}")
        return None

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f'Комментрий от {self.author} к {self.post}'

class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['post', 'user'],  # Для авторизованных пользователей
            ['post', 'session_key'],  # Для анонимых пользователей
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
    CONTACTS_PAGE = 'contacts'
    CREATE_POST_PAGE = 'create_post'
    ABOUT_PAGE = 'about'
    
    PAGE_CHOICES = [
        (CONTACTS_PAGE, 'Страница "Связь со мной"'),
        (CREATE_POST_PAGE, 'Создание постов'),
        (ABOUT_PAGE, 'О сайте')
    ]
    
    page_name = models.CharField(max_length=100, unique=True, choices=PAGE_CHOICES)
    is_active = models.BooleanField(default=True)
    disabled_message = models.TextField(default='Страница временно недоступна')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Настройка страницы'
        verbose_name_plural = 'Настройки страниц'

    def __str__(self):
        return f"{self.get_page_name_display()} ({'Активна' if self.is_active else 'Отключена'})"

class TextTemplate(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50, default='general')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Story(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    cover = CloudinaryField('cover',
        folder='stories/covers/',
        null=True,
        blank=True,
        transformation={
            'width': 800,
            'height': 1200,
            'crop': 'fill',
            'gravity': 'center'
        }
    )
    title = models.CharField(max_length=200)
    alt_title = models.CharField(max_length=200, blank=True)
    alt_titles = models.JSONField(default=list, blank=True)  # Для хранения дополнительных названий
    chapters_count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)
    description = models.TextField()
    link_title = models.CharField(max_length=200, blank=True)
    link_url = models.URLField(blank=True)
    additional_links = models.JSONField(default=list, blank=True)  # Для хранения дополнительных ссылок
    is_draft = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'История'
        verbose_name_plural = 'Истории'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:story_detail', kwargs={'pk': self.pk})

    def get_cover_url(self):
        if self.cover:
            return self.cover.url
        return None