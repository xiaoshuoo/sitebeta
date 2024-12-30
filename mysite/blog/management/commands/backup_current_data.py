from django.core.management.base import BaseCommand
import psycopg2
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Создание резервной копии текущих данных'

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
            cursor = conn.cursor()

            # Получаем данные из всех таблиц
            tables = [
                'auth_user',
                'blog_profile',
                'blog_category',
                'blog_tag',
                'blog_post',
                'blog_comment',
                'blog_postview',
                'blog_invitecode',
                'blog_title'
            ]

            backup_data = {}

            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                backup_data[table] = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    # Преобразуем datetime в строку
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    backup_data[table].append(row_dict)

            # Сохраняем в файл
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'backup_{timestamp}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            self.stdout.write(self.style.SUCCESS(f'Бэкап успешно создан: {filename}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при создании бэкапа: {str(e)}'))
        finally:
            cursor.close()
            conn.close() 