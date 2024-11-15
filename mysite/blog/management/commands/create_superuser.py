from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a superuser automatically'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='Odinochka',
                email='admin@example.com',
                password='1'  # Измените на свой безопасный пароль
            )
            self.stdout.write(self.style.SUCCESS('Superuser has been created'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists')) 