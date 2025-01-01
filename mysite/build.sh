#!/bin/bash
# exit on error
set -o errexit

# Создаем необходимые директории
mkdir -p staticfiles
mkdir -p static/css
mkdir -p media

# Устанавливаем зависимости
python -m pip install --upgrade pip
pip install -r requirements.txt

# Устанавливаем node и npm если их нет
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
    apt-get install -y nodejs
fi

# Устанавливаем зависимости npm
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
npm install @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio

# Собираем Tailwind CSS
npx tailwindcss -i static/css/main.css -o static/css/dist/main.css --minify

# Собираем статические файлы Django
python manage.py collectstatic --noinput
python manage.py compress --force

# Применяем миграции
python manage.py migrate
