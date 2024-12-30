from django.core.management.base import BaseCommand
import psycopg2
from django.contrib.auth.models import User
from blog.models import Profile, Post, Category, Tag, Comment, PostView, Title, TextTemplate
from django.db import connection

class Command(BaseCommand):
    help = 'Проверка и восстановление базы данных'

    def handle(self, *args, **options):
        try:
            # Проверяем подключение
            conn = psycopg2.connect(
                dbname='django_blog_7f9a',
                user='django_blog_7f9a_user',
                password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                port='5432',
                sslmode='require'
            )
            cursor = conn.cursor()

            # Проверяем существующие таблицы
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            existing_tables = [table[0] for table in cursor.fetchall()]
            self.stdout.write(f"Существующие таблицы: {existing_tables}")

            # Проверяем количество записей в каждой таблице
            for table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                self.stdout.write(f"Таблица {table}: {count} записей")

            # Проверяем и восстанавливаем связи
            cursor.execute("""
                SELECT conname, conrelid::regclass, confrelid::regclass
                FROM pg_constraint
                WHERE contype = 'f'
            """)
            foreign_keys = cursor.fetchall()
            self.stdout.write(f"Внешние ключи: {foreign_keys}")

            # Проверяем индексы
            cursor.execute("""
                SELECT tablename, indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public'
            """)
            indexes = cursor.fetchall()
            self.stdout.write(f"Индексы: {indexes}")

            # Проверяем и исправляем последовательности
            cursor.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public'
            """)
            sequences = cursor.fetchall()
            for seq in sequences:
                cursor.execute(f"SELECT setval('{seq[0]}', (SELECT COALESCE(MAX(id), 1) FROM {seq[0].split('_id_seq')[0]}))")

            # Проверяем размер базы данных
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            db_size = cursor.fetchone()[0]
            self.stdout.write(f"Размер базы данных: {db_size}")

            # Проверяем активные подключения
            cursor.execute("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """)
            connections = cursor.fetchone()[0]
            self.stdout.write(f"Активные подключения: {connections}")

            cursor.close()
            conn.close()

            self.stdout.write(self.style.SUCCESS('Проверка и восстановление завершены успешно'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}')) 