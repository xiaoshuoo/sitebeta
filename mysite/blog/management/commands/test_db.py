from django.core.management.base import BaseCommand
from django.db import connection
import psycopg2

class Command(BaseCommand):
    help = 'Test database connection'

    def handle(self, *args, **options):
        try:
            # Проверяем подключение через Django
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('Django connection successful'))

            # Проверяем прямое подключение к PostgreSQL
            conn = psycopg2.connect(
                dbname='django_blog_7f9a',
                user='django_blog_7f9a_user',
                password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                port='5432',
                sslmode='require'
            )
            self.stdout.write(self.style.SUCCESS('Direct PostgreSQL connection successful'))
            
            # Проверяем версию PostgreSQL
            with conn.cursor() as cur:
                cur.execute('SELECT version();')
                version = cur.fetchone()[0]
                self.stdout.write(f'PostgreSQL version: {version}')
            
            conn.close()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Connection failed: {str(e)}')) 