from django.core.management.base import BaseCommand
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates necessary media directories'

    def handle(self, *args, **options):
        media_dirs = [
            'avatars',
            'posts',
            'posts/content',
            'covers',
            'thumbnails'
        ]
        
        for directory in media_dirs:
            path = os.path.join(settings.MEDIA_ROOT, directory)
            os.makedirs(path, exist_ok=True)
            if not settings.DEBUG:
                os.chmod(path, 0o777)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created directory: {path}')
            ) 