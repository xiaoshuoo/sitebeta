from django.core.management.base import BaseCommand
from blog.models import TextTemplate

class Command(BaseCommand):
    help = 'Обновляет типы шаблонов для существующих шаблонов Gutierrez и Rossi'

    def handle(self, *args, **options):
        # Обновляем шаблоны Rossi
        rossi_templates = TextTemplate.objects.filter(
            created_by=None,
            category='rossi',
            template_type__isnull=True
        )
        rossi_count = rossi_templates.count()
        for template in rossi_templates:
            template.template_type = 'rossi'
            template.save(update_fields=['template_type'])
        self.stdout.write(self.style.SUCCESS(f'Обновлено {rossi_count} шаблонов Rossi'))

        # Обновляем шаблоны Gutierrez (все остальные публичные шаблоны без типа)
        gutierrez_templates = TextTemplate.objects.filter(
            created_by=None,
            template_type__isnull=True
        ).exclude(category='rossi')
        gutierrez_count = gutierrez_templates.count()
        for template in gutierrez_templates:
            template.template_type = 'gutierrez'
            template.save(update_fields=['template_type'])
        self.stdout.write(self.style.SUCCESS(f'Обновлено {gutierrez_count} шаблонов Gutierrez'))

        self.stdout.write(self.style.SUCCESS(f'Всего обновлено {rossi_count + gutierrez_count} шаблонов')) 