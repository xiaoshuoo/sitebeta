#!/bin/bash

# Создаем бэкап
python scripts/backup.py

# Копируем медиафайлы
timestamp=$(date +%Y%m%d_%H%M%S)
tar -czf "backups/media_${timestamp}.tar.gz" media/

# Удаляем старые бэкапы (оставляем последние 5)
cd backups
ls -t *.json | tail -n +6 | xargs -r rm
ls -t *.tar.gz | tail -n +6 | xargs -r rm 