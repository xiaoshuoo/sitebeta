import os
import sys
import django
import json
from datetime import datetime
from django.core.serializers import serialize
from django.core.management import call_command

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import Post, Category, Tag, UserProfile, PostView

def backup_database():
    # Создаем директорию для бэкапов если её нет
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Имя файла с текущей датой
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')
    
    # Создаем бэкап всех моделей
    models = [Post, Category, Tag, UserProfile, PostView]
    backup_data = {}
    
    for model in models:
        backup_data[model.__name__] = json.loads(serialize('json', model.objects.all()))
    
    # Сохраняем бэкап в файл
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    print(f'Backup created: {backup_file}')

def restore_database(backup_file):
    # Загружаем данные из бэкапа
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    # Очищаем существующие данные
    PostView.objects.all().delete()
    Post.objects.all().delete()
    Tag.objects.all().delete()
    Category.objects.all().delete()
    UserProfile.objects.all().delete()
    
    # Восстанавливаем данные
    for model_name, objects in backup_data.items():
        model = globals()[model_name]
        for obj in objects:
            fields = obj['fields']
            if 'id' in obj:
                fields['id'] = obj['id']
            model.objects.create(**fields)
    
    print(f'Database restored from: {backup_file}')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if len(sys.argv) > 2:
            restore_database(sys.argv[2])
        else:
            print('Please specify backup file to restore')
    else:
        backup_database() 