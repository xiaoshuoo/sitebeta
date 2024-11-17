from django.core.management.base import BaseCommand
from django.core import serializers
from blog.models import Profile, Post, Category, Tag, Comment, PostView
from django.contrib.auth.models import User
import json

class Command(BaseCommand):
    help = 'Import all data from JSON file'

    def handle(self, *args, **options):
        try:
            with open('data_export.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Очищаем существующие данные
            PostView.objects.all().delete()
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.all().delete()

            # Импортируем пользователей
            for user_data in data['users']:
                User.objects.create(**user_data['fields'])

            # Импортируем профили
            for profile_data in data['profiles']:
                Profile.objects.create(**profile_data['fields'])

            # Импортируем категории
            for category_data in data['categories']:
                Category.objects.create(**category_data['fields'])

            # Импортируем теги
            for tag_data in data['tags']:
                Tag.objects.create(**tag_data['fields'])

            # Импортируем посты
            for post_data in data['posts']:
                Post.objects.create(**post_data['fields'])

            # Импортируем комментарии
            for comment_data in data['comments']:
                Comment.objects.create(**comment_data['fields'])

            # Импортируем просмотры
            for view_data in data['post_views']:
                PostView.objects.create(**view_data['fields'])

            self.stdout.write(self.style.SUCCESS('Successfully imported all data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}')) 