from django.core.management.base import BaseCommand
from django.db import connection
import psycopg2
import time

class Command(BaseCommand):
    help = 'Fix database connection issues'

    def handle(self, *args, **options):
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                self.stdout.write("Checking database connection...")
                
                # Проверяем подключение через Django
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    self.stdout.write(self.style.SUCCESS("Django connection successful"))
                
                # Проверяем прямое подключение к PostgreSQL
                conn = psycopg2.connect(
                    dbname='django_blog_7f9a',
                    user='django_blog_7f9a_user',
                    password='qNKOalXZlLxzA7rlrYmbkN96ZJ6oHbbE',
                    host='dpg-csrl8f1u0jms7392hlrg-a.oregon-postgres.render.com',
                    port='5432',
                    sslmode='require'
                )
                
                # Проверяем состояние БД
                with conn.cursor() as cur:
                    # Проверяем версию PostgreSQL
                    cur.execute('SELECT version();')
                    version = cur.fetchone()[0]
                    self.stdout.write(f"PostgreSQL version: {version}")
                    
                    # Проверяем активные подключения
                    cur.execute("""
                        SELECT count(*) FROM pg_stat_activity 
                        WHERE datname = current_database();
                    """)
                    connections = cur.fetchone()[0]
                    self.stdout.write(f"Active connections: {connections}")
                    
                    # Проверяем размер базы данных
                    cur.execute("""
                        SELECT pg_size_pretty(pg_database_size(current_database()));
                    """)
                    db_size = cur.fetchone()[0]
                    self.stdout.write(f"Database size: {db_size}")
                    
                    # Проверяем и восстанавливаем последовательности
                    cur.execute("""
                        SELECT schemaname, tablename, columnname 
                        FROM pg_get_serial_sequences();
                    """)
                    sequences = cur.fetchall()
                    for schema, table, column in sequences:
                        cur.execute(f"""
                            SELECT setval(
                                pg_get_serial_sequence('{schema}.{table}', '{column}'),
                                COALESCE((SELECT MAX({column}) FROM {schema}.{table}), 1)
                            );
                        """)
                
                conn.close()
                self.stdout.write(self.style.SUCCESS("Database connection fixed successfully"))
                break
                
            except Exception as e:
                attempt += 1
                self.stdout.write(self.style.WARNING(f"Attempt {attempt} failed: {str(e)}"))
                if attempt < max_attempts:
                    self.stdout.write("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    self.stdout.write(self.style.ERROR("Failed to fix database connection")) 