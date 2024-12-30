from django.core.management.base import BaseCommand
from django.db import connections
import psycopg2
import time

class Command(BaseCommand):
    help = 'Проверка подключения к базе данных'

    def handle(self, *args, **options):
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                self.stdout.write("Проверяем подключение к базе данных...")
                
                # Пробуем прямое подключение к PostgreSQL
                conn = psycopg2.connect(
                    dbname='b3fbgpfjiisirtqyqdry',
                    user='utihi7xqxpcfj2b5nzxr',
                    password='JMq9iLTaBX23jV4oFu9JsIqHIO45dB',
                    host='b3fbgpfjiisirtqyqdry-postgresql.services.clever-cloud.com',
                    port='50013',
                    sslmode='require'
                )
                
                # Проверяем состояние БД
                with conn.cursor() as cur:
                    # Проверяем версию PostgreSQL
                    cur.execute('SELECT version();')
                    version = cur.fetchone()[0]
                    self.stdout.write(f"Версия PostgreSQL: {version}")
                    
                    # Проверяем количество подключений
                    cur.execute("""
                        SELECT count(*) FROM pg_stat_activity 
                        WHERE datname = current_database();
                    """)
                    connections = cur.fetchone()[0]
                    self.stdout.write(f"Активных подключений: {connections}")
                
                conn.close()
                self.stdout.write(self.style.SUCCESS("Подключение к базе данных успешно"))
                break
                
            except Exception as e:
                attempt += 1
                self.stdout.write(self.style.WARNING(f"Попытка {attempt} не удалась: {str(e)}"))
                if attempt < max_attempts:
                    self.stdout.write("Повторная попытка через 5 секунд...")
                    time.sleep(5)
                else:
                    self.stdout.write(self.style.ERROR("Не удалось подключиться к базе данных")) 