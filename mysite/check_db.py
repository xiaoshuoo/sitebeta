import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

db_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

try:
    conn = psycopg2.connect(**db_params)
    print("Successfully connected to the database!")
    conn.close()
except Exception as e:
    print(f"Error connecting to the database: {e}") 