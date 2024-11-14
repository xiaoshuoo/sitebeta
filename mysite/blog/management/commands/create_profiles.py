from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile

class Command(BaseCommand):
    help = 'Creates profiles for users that do not have one'

    def handle(self, *args, **options):
        users = User.objects.all()
        created = 0
        for user in users:
            profile, was_created = Profile.objects.get_or_create(user=user)
            if was_created:
                created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created} profiles'
            )
        ) 