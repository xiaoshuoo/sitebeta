from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile, Post, Category, Tag, Comment, PostView
from django.db.models import Count
from django.utils import timezone

class Command(BaseCommand):
    help = 'Synchronize and check database data'

    def handle(self, *args, **options):
        self.stdout.write("Starting data synchronization...")

        # Проверяем и создаем профили для всех пользователей
        users = User.objects.all()
        self.stdout.write(f"Found {users.count()} users")
        
        for user in users:
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(f"Created profile for user {user.username}")

        # Проверяем категории
        categories = Category.objects.all()
        self.stdout.write(f"Found {categories.count()} categories")
        
        # Проверяем посты и их связи
        posts = Post.objects.all()
        self.stdout.write(f"Found {posts.count()} posts")
        
        for post in posts:
            # Проверяем автора
            if not post.author:
                self.stdout.write(self.style.WARNING(f"Post {post.id} has no author"))
                continue
                
            # Проверяем и обновляем счетчик просмотров
            views_count = PostView.objects.filter(post=post).count()
            if post.views_count != views_count:
                post.views_count = views_count
                post.save()
                self.stdout.write(f"Updated views count for post {post.id}")
                
            # Проверяем комментарии
            comments_count = Comment.objects.filter(post=post).count()
            self.stdout.write(f"Post {post.id} has {comments_count} comments")

        # Обновляем статистику
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_posts = Post.objects.count()
        published_posts = Post.objects.filter(is_published=True).count()
        total_comments = Comment.objects.count()
        
        self.stdout.write("\nStatistics:")
        self.stdout.write(f"Total users: {total_users}")
        self.stdout.write(f"Active users: {active_users}")
        self.stdout.write(f"Total posts: {total_posts}")
        self.stdout.write(f"Published posts: {published_posts}")
        self.stdout.write(f"Total comments: {total_comments}")

        # Проверяем и исправляем счетчики
        categories_with_counts = Category.objects.annotate(
            real_count=Count('post')
        )
        
        for category in categories_with_counts:
            self.stdout.write(f"\nCategory: {category.name}")
            self.stdout.write(f"Posts count: {category.real_count}")

        self.stdout.write(self.style.SUCCESS("\nData synchronization completed")) 