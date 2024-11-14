from django.core.management.base import BaseCommand
from blog.models import Post
from django.utils.text import slugify
import random
import string

def generate_unique_slug(title, Post):
    base_slug = slugify(title)
    unique_slug = base_slug
    counter = 1
    while Post.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1
    return unique_slug

class Command(BaseCommand):
    help = 'Заполняет пустые slug у постов'

    def handle(self, *args, **options):
        posts = Post.objects.filter(slug='')
        for post in posts:
            if post.title:
                post.slug = generate_unique_slug(post.title, Post)
            else:
                # Если нет заголовка, генерируем случайный slug
                random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                post.slug = generate_unique_slug(f"post-{random_string}", Post)
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Создан slug "{post.slug}" для поста "{post.title}"')) 