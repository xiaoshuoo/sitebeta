from django.db.models.signals import post_save, pre_delete, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Post, Category, Tag, Comment
import os
from django.db import connection

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль пользователя при создании пользователя"""
    if created:
        # Проверяем, существует ли уже профиль
        if not Profile.objects.filter(user=instance).exists():
            Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль пользователя при сохранении пользователя"""
    try:
        profile = Profile.objects.get(user=instance)
        profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Post)
def update_post_relations(sender, instance, created, **kwargs):
    """Обновляет связанные данные при сохранении поста"""
    # Обновляем счетчик постов в категории
    if instance.category:
        instance.category.save()
    
    # Обновляем теги
    if created:
        words = set(word.lower() for word in instance.content.split() if len(word) > 4)
        for word in words:
            if word.isalnum():
                tag, _ = Tag.objects.get_or_create(
                    name=word.capitalize(),
                    defaults={'slug': word.lower()}
                )
                instance.tags.add(tag)

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    """Создает базовые категории после миграции"""
    if sender.name == 'blog':
        from .models import Category
        default_categories = [
            {
                'name': 'Общее',
                'slug': 'general',
                'description': 'Общие посты',
                'icon': 'fa-globe'
            },
            {
                'name': 'Новости',
                'slug': 'news',
                'description': 'Новости сайта',
                'icon': 'fa-newspaper'
            }
        ]
        
        for category_data in default_categories:
            Category.objects.get_or_create(
                slug=category_data['slug'],
                defaults=category_data
            )

@receiver(pre_delete, sender=Profile)
def delete_profile_files(sender, instance, **kwargs):
    """Удаляет файлы профиля при удалении профиля"""
    try:
        if instance.avatar and os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)
        if instance.cover and os.path.isfile(instance.cover.path):
            os.remove(instance.cover.path)
    except Exception as e:
        print(f"Error deleting profile files: {str(e)}")

@receiver(pre_delete, sender=Post)
def delete_post_files(sender, instance, **kwargs):
    """Удаляет файлы поста при удалении поста"""
    try:
        if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
    except Exception as e:
        print(f"Error deleting post files: {str(e)}")

def ensure_database_connections():
    """Проверяет и восстанавливает подключения к базе данных"""
    try:
        connection.ensure_connection()
    except Exception as e:
        print(f"Error ensuring database connection: {str(e)}")
        # Пробуем переподключиться
        connection.connect()