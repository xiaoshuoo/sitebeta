from django.core.management.base import BaseCommand
from django.db import connection
import psycopg2

class Command(BaseCommand):
    help = 'Check database connection status and settings'

    def handle(self, *args, **options):
        try:
            # Получаем информацию о текущих настройках
            db_settings = connection.settings_dict
            self.stdout.write("Database settings:")
            self.stdout.write(f"ENGINE: {db_settings['ENGINE']}")
            self.stdout.write(f"NAME: {db_settings['NAME']}")
            self.stdout.write(f"USER: {db_settings['USER']}")
            self.stdout.write(f"HOST: {db_settings['HOST']}")
            self.stdout.write(f"PORT: {db_settings['PORT']}")
            
            # Проверяем прямое подключение
            conn = psycopg2.connect(
                dbname=db_settings['NAME'],
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                host=db_settings['HOST'],
                port=db_settings['PORT'],
                sslmode='require'
            )
            
            # Проверяем версию PostgreSQL
            with conn.cursor() as cur:
                cur.execute('SELECT version();')
                version = cur.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'PostgreSQL version: {version}'))
                
                # Проверяем размер базы данных
                cur.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()));
                """)
                db_size = cur.fetchone()[0]
                self.stdout.write(f'Database size: {db_size}')
                
                # Проверяем количество подключений
                cur.execute("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE datname = current_database();
                """)
                connections = cur.fetchone()[0]
                self.stdout.write(f'Active connections: {connections}')
                
                # Проверяем список таблиц
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                tables = cur.fetchall()
                self.stdout.write('\nDatabase tables:')
                for table in tables:
                    self.stdout.write(f'- {table[0]}')
            
            conn.close()
            self.stdout.write(self.style.SUCCESS('\nDatabase connection successful'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database connection failed: {str(e)}')) 