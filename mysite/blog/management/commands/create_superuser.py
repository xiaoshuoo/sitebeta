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
                    password='admin',
                    first_name='Admin',
                    last_name='User'
                )
                
                if not Profile.objects.filter(user=superuser).exists():
                    Profile.objects.create(
                        user=superuser,
                        role='creator',
                        bio='Администратор сайта',
                        location='System',
                        occupation='Site Administrator'
                    )
                
                self.stdout.write(self.style.SUCCESS(
                    f'Superuser created successfully\n'
                    f'Username: admin\n'
                    f'Password: admin\n'
                    f'Email: admin@example.com\n'
                    f'Role: creator'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists')) 