from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile, Post, Category, Tag, Comment, PostView
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime

class Command(BaseCommand):
    help = 'Export data from local SQLite to JSON'

    def handle(self, *args, **options):
        try:
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
            for user in User.objects.all():
                data['users'].append({
                    'username': user.username,
                    'email': user.email,
                    'password': user.password,
                    'is_superuser': user.is_superuser,
                    'is_staff': user.is_staff,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.isoformat(),
                    'first_name': user.first_name,
                    'last_name': user.last_name
                })

            # Экспортируем профили
            for profile in Profile.objects.all():
                data['profiles'].append({
                    'user_id': profile.user.id,
                    'avatar': str(profile.avatar) if profile.avatar else None,
                    'cover': str(profile.cover) if profile.cover else None,
                    'bio': profile.bio,
                    'location': profile.location,
                    'website': profile.website,
                    'occupation': profile.occupation,
                    'role': profile.role
                })

            # Экспортируем категории
            for category in Category.objects.all():
                data['categories'].append({
                    'name': category.name,
                    'slug': category.slug,
                    'description': category.description,
                    'icon': category.icon,
                    'created_at': category.created_at.isoformat() if category.created_at else None,
                    'updated_at': category.updated_at.isoformat() if category.updated_at else None,
                    '_posts_count': category._posts_count
                })

            # Экспортируем посты
            for post in Post.objects.all():
                data['posts'].append({
                    'title': post.title,
                    'slug': post.slug,
                    'content': post.content,
                    'created_at': post.created_at.isoformat(),
                    'updated_at': post.updated_at.isoformat(),
                    'author_id': post.author.id,
                    'category_id': post.category.id if post.category else None,
                    'thumbnail': str(post.thumbnail) if post.thumbnail else None,
                    'is_published': post.is_published,
                    'views_count': post.views_count
                })

            # Сохраняем в файл
            with open('local_data_export.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=DjangoJSONEncoder)

            self.stdout.write(self.style.SUCCESS('Successfully exported data to local_data_export.json'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error exporting data: {str(e)}')) 