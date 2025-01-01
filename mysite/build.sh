#!/bin/bash
# exit on error
set -o errexit

# Создаем необходимые директории
mkdir -p staticfiles
mkdir -p static/css/dist
mkdir -p media

# Устанавливаем зависимости Python
python -m pip install --upgrade pip
pip install -r requirements.txt

# Устанавливаем Node.js через nvm
export NVM_DIR="$HOME/.nvm"
mkdir -p $NVM_DIR
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
. "$NVM_DIR/nvm.sh"
nvm install 16
nvm use 16

# Очищаем npm кэш и node_modules
rm -rf node_modules
npm cache clean --force

# Устанавливаем зависимости npm и собираем CSS
npm install --no-optional

# Копируем custom.css в директорию dist
cp static/css/custom.css static/css/dist/

# Собираем Tailwind CSS
NODE_ENV=production npx tailwindcss -i ./static/css/main.css -o ./static/css/dist/main.css --minify

# Собираем статические файлы Django
python manage.py collectstatic --noinput

# Применяем миграции
python manage.py migrate
