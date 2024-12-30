from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import psycopg2

class Command(BaseCommand):
    help = 'Проверка подключения к базе данных'

    def handle(self, *args, **options):
        try:
            # Пробуем прямое подключение к PostgreSQL
            conn = psycopg2.connect(
                dbname='django_blog_7f9a',
                user='django_blog_7f9a_user',
                password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                port='5432',
                sslmode='require'
            )
            
            # Проверяем версию PostgreSQL
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            
            # Проверяем размер базы данных
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            db_size = cursor.fetchone()[0]
            
            # Проверяем количество подключений
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database()
            """)
            connections_count = cursor.fetchone()[0]
            
            self.stdout.write(self.style.SUCCESS(f'База данных доступна'))
            self.stdout.write(f'Версия PostgreSQL: {version}')
            self.stdout.write(f'Размер базы данных: {db_size}')
            self.stdout.write(f'Активных подключений: {connections_count}')
            
            cursor.close()
            conn.close()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка подключения: {str(e)}')) 