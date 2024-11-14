from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал для создания или обновления профиля пользователя
    """
    if created:
        # Создаем новый профиль только если пользователь только что создан
        Profile.objects.create(
            user=instance,
            bio='',
            location='',
            occupation=''
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)