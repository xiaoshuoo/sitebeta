from django.core.management.base import BaseCommand
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Command(BaseCommand):
    help = 'Сброс базы данных PostgreSQL'

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
            
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Удаляем все таблицы
            cursor.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)

            # Удаляем все последовательности
            cursor.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT sequencename FROM pg_sequences WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequencename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)

            cursor.close()
            conn.close()

            self.stdout.write(self.style.SUCCESS('База данных успешно сброшена'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при сбросе базы данных: {str(e)}')) 