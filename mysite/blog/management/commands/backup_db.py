from django.core.management.base import BaseCommand
from django.core.management import call_command
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Creates a database backup'

    def handle(self, *args, **kwargs):
        # Создаем директорию для бэкапов если её нет
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Создаем имя файла с текущей датой
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.json')

        try:
            # Создаем бэкап
            with open(backup_file, 'w') as f:
                call_command('dumpdata', exclude=['contenttypes', 'auth.permission'], indent=2, stdout=f)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created backup at {backup_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Backup failed: {str(e)}')
            ) 