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

# Устанавливаем зависимости npm и собираем CSS
npm install
npm run build

# Собираем статические файлы Django
python manage.py collectstatic --noinput

# Применяем миграции
python manage.py migrate
