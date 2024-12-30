from django.core.management.base import BaseCommand
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = 'Синхронизация статических файлов'

    def handle(self, *args, **options):
        try:
            # Синхронизируем статические файлы
            for directory in settings.STATIC_DIRS:
                local_dir = os.path.join(settings.BASE_DIR, 'static', directory)
                server_dir = os.path.join(settings.STATIC_ROOT, directory)
                
                # Создаем директории если их нет
                os.makedirs(local_dir, exist_ok=True)
                if not settings.DEBUG:
                    os.makedirs(server_dir, exist_ok=True)
                    os.chmod(server_dir, 0o777)
                
                # Копируем файлы
                for root, dirs, files in os.walk(local_dir):
                    for file in files:
                        src = os.path.join(root, file)
                        dst = os.path.join(server_dir, file)
                        shutil.copy2(src, dst)
                        if not settings.DEBUG:
                            os.chmod(dst, 0o644)
                        self.stdout.write(f'Скопирован файл: {file}')
            
            self.stdout.write(self.style.SUCCESS('Статические файлы успешно синхронизированы'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при синхронизации: {str(e)}')) 