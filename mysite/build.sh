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

# Устанавливаем nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Устанавливаем Node.js
nvm install 18
nvm use 18

# Устанавливаем зависимости npm
npm install

# Собираем Tailwind CSS
npx tailwindcss -i static/css/main.css -o static/css/dist/main.css --minify

# Собираем статические файлы Django
python manage.py collectstatic --noinput

# Применяем миграции
python manage.py migrate
