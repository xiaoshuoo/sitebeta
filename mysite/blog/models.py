from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor.fields import RichTextField
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Описание")
    icon = models.CharField(max_length=50, default="fa-folder")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def posts_count(self):
        return self.posts.filter(is_published=True).count()

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='post_thumbnails/', null=True, blank=True, verbose_name="Обложка поста")
    attachments = models.ManyToManyField('PostAttachment', blank=True, related_name='posts')
    views_count = models.PositiveIntegerField(default=0)
    is_locked = models.BooleanField(default=False, verbose_name="Заблокирован")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.title

class InviteCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invites')
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_invite')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Код приглашения"
        verbose_name_plural = "Коды пиглашения"

    def __str__(self):
        return f"Код: {self.code} ({self.created_by.username})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    interests = models.ManyToManyField('Tag', blank=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    def __str__(self):
        return f"Профиль {self.user.username}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            
            while Tag.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        super().save(*args, **kwargs)

class PostAttachment(models.Model):
    file = models.FileField(upload_to='post_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)