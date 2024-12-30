from django.core.management.base import BaseCommand
from blog.models import PageSettings
from django.db import transaction

class Command(BaseCommand):
    help = 'Initialize basic settings'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Создаем базовые настройки страниц
                for page_name, page_title in PageSettings._meta.get_field('page_name').choices:
                    PageSettings.objects.get_or_create(
                        page_name=page_name,
                        defaults={
                            'is_active': True,
                            'disabled_message': f'Страница {page_title.lower()} временно недоступна'
                        }
                    )
                
                self.stdout.write(self.style.SUCCESS('Successfully initialized settings'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing settings: {str(e)}')) 