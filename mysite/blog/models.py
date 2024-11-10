from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from tinymce.models import HTMLField
from ckeditor_uploader.fields import RichTextUploadingField
import uuid
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    icon = models.CharField(max_length=50, default="fa-folder")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    @property
    def posts_count(self):
        return self.posts.filter(is_published=True).count()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='post_thumbnails/', null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    views = models.ManyToManyField(User, through='PostView', related_name='viewed_posts')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.title

    def increment_views(self, user=None):
        """Увеличивает счетчик просмотров и записывает просмотр"""
        if user and user.is_authenticated:
            # Проверяем, не просматривал ли уже этот пользователь пост сегодня
            today = timezone.now().date()
            if not PostView.objects.filter(
                post=self,
                user=user,
                viewed_at__date=today
            ).exists():
                PostView.objects.create(post=self, user=user)
                self.views_count += 1
                self.save()
        else:
            # Для анонимных пользователей просто увеличиваем счетчик
            self.views_count += 1
            self.save()

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

class PostAttachment(models.Model):
    file = models.FileField(upload_to='post_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)

class PostView(models.Model):
    """Модель для отслеживания просмотров постов"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user', 'viewed_at')