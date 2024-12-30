from django.core.management.base import BaseCommand
import cloudinary
import cloudinary.uploader
import os
from django.conf import settings
from blog.models import Profile, Post

class Command(BaseCommand):
    help = 'Синхронизация медиа-файлов с Cloudinary'

    def handle(self, *args, **options):
        # Настраиваем Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )

        # Синхронизируем аватары
        profiles = Profile.objects.exclude(avatar='')
        for profile in profiles:
            if profile.avatar:
                try:
                    result = cloudinary.uploader.upload(
                        profile.avatar.path,
                        public_id=f"avatars/{os.path.basename(profile.avatar.name)}",
                        overwrite=True
                    )
                    self.stdout.write(f"Uploaded avatar for {profile.user.username}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error uploading avatar: {str(e)}"))

        # Синхронизируем миниатюры постов
        posts = Post.objects.exclude(thumbnail='')
        for post in posts:
            if post.thumbnail:
                try:
                    result = cloudinary.uploader.upload(
                        post.thumbnail.path,
                        public_id=f"thumbnails/{os.path.basename(post.thumbnail.name)}",
                        overwrite=True
                    )
                    self.stdout.write(f"Uploaded thumbnail for post: {post.title}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error uploading thumbnail: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Successfully synced media files with Cloudinary')) 