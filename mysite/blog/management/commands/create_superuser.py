from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            try:
                superuser = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin'
                )
                # Проверяем существование профиля
                if not Profile.objects.filter(user=superuser).exists():
                    Profile.objects.create(user=superuser)
                self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists')) 