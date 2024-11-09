import os

# Создаем директории
directories = [
    'static/css',
    'static/js',
    'static/img',
    'staticfiles',
    'media'
]

# Создаем директории, если они не существуют
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f'Created directory: {directory}')

# Создаем .gitkeep файлы
gitkeep_files = [
    'static/css/.gitkeep',
    'static/js/.gitkeep',
    'static/img/.gitkeep',
    'staticfiles/.gitkeep',
    'media/.gitkeep'
]

# Создаем .gitkeep файлы
for file_path in gitkeep_files:
    with open(file_path, 'w') as f:
        pass  # Создаем пустой файл
    print(f'Created file: {file_path}')