from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile, Post, Category, Tag, Comment, PostView
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Command(BaseCommand):
    help = 'Очистка базы данных PostgreSQL'

    def handle(self, *args, **options):
        try:
            # Подключаемся к PostgreSQL
            conn = psycopg2.connect(
                dbname='django_blog_7f9a',
                user='django_blog_7f9a_user',
                password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                port='5432',
                sslmode='require'
            )
            
            # Устанавливаем уровень изоляции
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Получаем список существующих таблиц
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            existing_tables = [table[0] for table in cursor.fetchall()]

            # Порядок очистки таблиц с учетом зависимостей
            tables_to_clear = [
                'blog_postview',
                'blog_comment',
                'blog_post_tags',
                'blog_post',
                'blog_tag',
                'blog_category',
                'blog_profile',
                'blog_invitecode',
                'blog_pagesettings',
                'auth_user'
            ]

            # Очищаем только существующие таблицы
            for table_name in tables_to_clear:
                if table_name in existing_tables:
                    try:
                        # Очищаем таблицу
                        cursor.execute(f'DELETE FROM "{table_name}";')
                        
                        # Сбрасываем счетчик ID, если есть
                        try:
                            cursor.execute(f'ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;')
                        except:
                            pass  # Игнорируем ошибку, если последовательность не существует
                            
                        self.stdout.write(self.style.SUCCESS(f'Очищена таблица {table_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Ошибка при очистке таблицы {table_name}: {str(e)}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'Таблица {table_name} не существует'))

            cursor.close()
            conn.close()

            self.stdout.write(self.style.SUCCESS('База данных успешно очищена'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при очистке базы данных: {str(e)}')) 