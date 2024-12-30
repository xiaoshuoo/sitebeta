import psycopg2
from psycopg2 import OperationalError
import os

def test_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRESQL_ADDON_DB'),
            user=os.getenv('POSTGRESQL_ADDON_USER'),
            password=os.getenv('POSTGRESQL_ADDON_PASSWORD'),
            host=os.getenv('POSTGRESQL_ADDON_HOST'),
            port=os.getenv('POSTGRESQL_ADDON_PORT'),
            sslmode='require'
        )
        print("Подключение к PostgreSQL успешно!")
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        print(f"Версия PostgreSQL: {db_version[0]}")
        cursor.close()
        conn.close()
    except OperationalError as e:
        print(f"Ошибка при подключении к PostgreSQL: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    test_connection() 