from django.core.management.base import BaseCommand
from django.core import serializers
from blog.models import Profile, Post, Category, Tag, Comment, PostView
from django.contrib.auth.models import User
import json

class Command(BaseCommand):
    help = 'Export all data to JSON file'

    def handle(self, *args, **options):
        # Словарь для хранения всех данных
        data = {
            'users': [],
            'profiles': [],
            'categories': [],
            'tags': [],
            'posts': [],
            'comments': [],
            'post_views': []
        }

        # Экспортируем пользователей
        users = User.objects.all()
        data['users'] = json.loads(serializers.serialize('json', users))

        # Экспортируем профили
        profiles = Profile.objects.all()
        data['profiles'] = json.loads(serializers.serialize('json', profiles))

        # Экспортируем категории
        categories = Category.objects.all()
        data['categories'] = json.loads(serializers.serialize('json', categories))

        # Экспортируем теги
        tags = Tag.objects.all()
        data['tags'] = json.loads(serializers.serialize('json', tags))

        # Экспортируем посты
        posts = Post.objects.all()
        data['posts'] = json.loads(serializers.serialize('json', posts))

        # Экспортируем комментарии
        comments = Comment.objects.all()
        data['comments'] = json.loads(serializers.serialize('json', comments))

        # Экспортируем просмотры
        post_views = PostView.objects.all()
        data['post_views'] = json.loads(serializers.serialize('json', post_views))

        # Сохраняем в файл
        with open('data_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS('Successfully exported all data')) 