from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from blog.models import Profile, Category, Tag, Post, Comment
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize database and create initial data'

    def handle(self, *args, **options):
        try:
            self.stdout.write("Checking database connection...")
            
            # Проверяем подключение
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS("Database connection successful"))
                
                # Проверяем существующие таблицы
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cursor.fetchall()
                self.stdout.write(f"Found tables: {[table[0] for table in tables]}")
                
                # Проверяем и создаем необходимые расширения
                cursor.execute("""
                    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
                """)
                
            # Создаем базовые категории если их нет
            categories = [
                {'name': 'Общее', 'slug': 'general', 'posts_count': 0},
                {'name': 'Новости', 'slug': 'news', 'posts_count': 0},
                {'name': 'Статьи', 'slug': 'articles', 'posts_count': 0},
            ]
            
            for cat_data in categories:
                Category.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults={
                        'name': cat_data['name'],
                        'posts_count': cat_data['posts_count']
                    }
                )
                
            # Создаем базовые теги
            tags = ['важное', 'интересное', 'обсуждение']
            for tag_name in tags:
                Tag.objects.get_or_create(
                    name=tag_name,
                    slug=tag_name
                )
                
            # Обновляем счетчики постов для всех категорий
            for category in Category.objects.all():
                category.update_posts_count()
                
            self.stdout.write(self.style.SUCCESS("Database initialized successfully"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error initializing database: {str(e)}"))
            logger.error(f"Database initialization error: {str(e)}") 