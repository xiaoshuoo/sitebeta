from dotenv import load_dotenv
import os

load_dotenv()

print("DATABASE_URL:", os.getenv('DATABASE_URL'))
print("DB_NAME:", os.getenv('DB_NAME'))
print("DB_USER:", os.getenv('DB_USER'))
print("DB_PASSWORD:", os.getenv('DB_PASSWORD'))
print("DB_HOST:", os.getenv('DB_HOST'))
print("DB_PORT:", os.getenv('DB_PORT')) 