import os
from pathlib import Path

# Получаем абсолютный путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent

# Обновляем пути к директориям
directories = [
    BASE_DIR / 'static' / 'css',
    BASE_DIR / 'static' / 'js',
    BASE_DIR / 'static' / 'img',
    BASE_DIR / 'staticfiles',
    BASE_DIR / 'media'
]

# Создаем директории, если они не существуют
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f'Created directory: {directory}')

# Создаем .gitkeep файлы
gitkeep_files = [
    BASE_DIR / 'static' / 'css' / '.gitkeep',
    BASE_DIR / 'static' / 'js' / '.gitkeep',
    BASE_DIR / 'static' / 'img' / '.gitkeep',
    BASE_DIR / 'staticfiles' / '.gitkeep',
    BASE_DIR / 'media' / '.gitkeep'
]

# Создаем .gitkeep файлы
for file_path in gitkeep_files:
    with open(file_path, 'w') as f:
        pass  # Создаем пустой файл
    print(f'Created file: {file_path}')