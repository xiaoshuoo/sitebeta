from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
import os

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
        # Проверяем существует ли профиль
        profile = Profile.objects.get(user=instance)
        profile.save()
    except Profile.DoesNotExist:
        # Если профиля нет, создаем его
        if not Profile.objects.filter(user=instance).exists():
            Profile.objects.create(user=instance)

@receiver(pre_delete, sender=Profile)
def delete_profile_files(sender, instance, **kwargs):
    """Удаляет файлы профиля при удалении профиля"""
    try:
        if instance.avatar:
            if os.path.isfile(instance.avatar.path):
                os.remove(instance.avatar.path)
        if instance.cover:
            if os.path.isfile(instance.cover.path):
                os.remove(instance.cover.path)
    except Exception as e:
        print(f"Error deleting profile files: {str(e)}")