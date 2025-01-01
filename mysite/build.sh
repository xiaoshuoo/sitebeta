#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка зависимостей Python
pip install -r requirements.txt

# Установка Node.js и npm
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Установка Tailwind CSS
npm install -D tailwindcss

# Инициализация Tailwind CSS
npx tailwindcss init

# Сборка CSS
npx tailwindcss -i ./static/src/input.css -o ./static/css/main.css --minify

# Сбор статических файлов Django
python manage.py collectstatic --no-input
