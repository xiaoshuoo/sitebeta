#!/bin/bash
# exit on error
set -o errexit

# Создаем необходимые директории
mkdir -p staticfiles
mkdir -p static/css
mkdir -p media

# Устанавливаем зависимости Python
python -m pip install --upgrade pip
pip install -r requirements.txt

# Устанавливаем Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Инициализируем npm проект если package.json не существует
if [ ! -f package.json ]; then
    npm init -y
fi

# Устанавливаем зависимости npm глобально
npm install -g tailwindcss postcss autoprefixer
npm install -g @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio

# Устанавливаем зависимости npm локально
npm install

# Создаем конфигурацию postcss если её нет
if [ ! -f postcss.config.js ]; then
    echo "module.exports = {
        plugins: {
            tailwindcss: {},
            autoprefixer: {},
        }
    }" > postcss.config.js
fi

# Собираем Tailwind CSS
NODE_ENV=production npx tailwindcss -i static/css/main.css -o static/css/dist/main.css --minify

# Собираем статические файлы Django
python manage.py collectstatic --noinput

# Применяем миграции
python manage.py migrate
