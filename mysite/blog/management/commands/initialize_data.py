from django.core.management.base import BaseCommand
from blog.models import Category, Tag
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Инициализация базовых данных (категории и теги)'

    def handle(self, *args, **options):
        # Базовые категории
        default_categories = [
            {
                'name': 'Программирование',
                'slug': 'programming',
                'description': 'Статьи о программировании',
                'icon': 'fa-code'
            },
            {
                'name': 'Веб-разработка',
                'slug': 'web-development',
                'description': 'Веб-разработка и технологии',
                'icon': 'fa-globe'
            },
            {
                'name': 'Дизайн',
                'slug': 'design',
                'description': 'UI/UX дизайн и графика',
                'icon': 'fa-paint-brush'
            },
            {
                'name': 'Технологии',
                'slug': 'tech',
                'description': 'Новости технологий',
                'icon': 'fa-microchip'
            }
        ]

        # Базовые теги
        default_tags = [
            'Python', 'JavaScript', 'HTML', 'CSS', 'Django',
            'React', 'Vue.js', 'Node.js', 'PostgreSQL', 'MySQL',
            'Git', 'Docker', 'Linux', 'AWS', 'DevOps'
        ]

        # Создаем категории
        for category_data in default_categories:
            Category.objects.get_or_create(
                slug=category_data['slug'],
                defaults={
                    'name': category_data['name'],
                    'description': category_data['description'],
                    'icon': category_data['icon']
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f'Категория "{category_data["name"]}" создана/обновлена')
            )

        # Создаем теги
        for tag_name in default_tags:
            Tag.objects.get_or_create(
                slug=slugify(tag_name),
                defaults={'name': tag_name}
            )
            self.stdout.write(
                self.style.SUCCESS(f'Тег "{tag_name}" создан/обновлен')
            ) 