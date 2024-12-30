from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Category, Tag, Title, Profile, Post
from django.db import transaction
from django.db.models.signals import post_save
from blog.utils import disable_signals

class Command(BaseCommand):
    help = 'Initialize database with default data'

    def handle(self, *args, **options):
        with disable_signals():
            try:
                with transaction.atomic():
                    # Создаем суперпользователя если его нет
                    if not User.objects.filter(username='Odinochka').exists():
                        admin_user = User.objects.create_superuser(
                            username='Odinochka',
                            email='admin@example.com',
                            password='1'
                        )
                        self.stdout.write(self.style.SUCCESS(f'Created superuser: {admin_user.username}'))

                        # Создаем профиль для админа только если его нет
                        if not Profile.objects.filter(user=admin_user).exists():
                            Profile.objects.create(
                                user=admin_user,
                                bio='Администратор сайта',
                                role='creator'
                            )
                    else:
                        admin_user = User.objects.get(username='Odinochka')
                        self.stdout.write(self.style.SUCCESS(f'Using existing superuser: {admin_user.username}'))

                    # Создаем категории если их нет
                    categories = [
                        {'name': 'Программирование', 'slug': 'programming', 'icon': 'fa-code'},
                        {'name': 'Дизайн', 'slug': 'design', 'icon': 'fa-palette'},
                        {'name': 'Технологии', 'slug': 'tech', 'icon': 'fa-microchip'},
                        {'name': 'Игры', 'slug': 'games', 'icon': 'fa-gamepad'},
                        {'name': 'Музыка', 'slug': 'music', 'icon': 'fa-music'},
                        {'name': 'Фильмы', 'slug': 'movies', 'icon': 'fa-film'},
                        {'name': 'Книги', 'slug': 'books', 'icon': 'fa-book'},
                    ]

                    for cat_data in categories:
                        category, created = Category.objects.get_or_create(
                            slug=cat_data['slug'],
                            defaults=cat_data
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created category: {cat_data["name"]}'))

                    # Создаем теги если их нет
                    tags = [
                        {'name': 'Python', 'slug': 'python'},
                        {'name': 'JavaScript', 'slug': 'javascript'},
                        {'name': 'Web Design', 'slug': 'web-design'},
                        {'name': 'AI', 'slug': 'ai'},
                        {'name': 'Machine Learning', 'slug': 'machine-learning'},
                        {'name': 'UI/UX', 'slug': 'ui-ux'},
                        {'name': 'Mobile', 'slug': 'mobile'},
                        {'name': 'DevOps', 'slug': 'devops'},
                        {'name': 'Security', 'slug': 'security'},
                        {'name': 'Cloud', 'slug': 'cloud'},
                    ]

                    for tag_data in tags:
                        if not Tag.objects.filter(slug=tag_data['slug']).exists():
                            Tag.objects.create(**tag_data)
                            self.stdout.write(self.style.SUCCESS(f'Created tag: {tag_data["name"]}'))

                    # Создаем титулы если их нет
                    titles = [
                        {
                            'name': 'Создатель',
                            'description': 'Создатель сайта',
                            'color': '#8B5CF6',
                            'icon': 'fas fa-crown'
                        },
                        {
                            'name': 'Модератор',
                            'description': 'Модератор сообщества',
                            'color': '#3B82F6',
                            'icon': 'fas fa-shield-alt'
                        },
                        {
                            'name': 'Эксперт',
                            'description': 'Эксперт в своей области',
                            'color': '#10B981',
                            'icon': 'fas fa-star'
                        },
                        {
                            'name': 'Активист',
                            'description': 'Активный участник сообщества',
                            'color': '#F59E0B',
                            'icon': 'fas fa-bolt'
                        },
                    ]

                    for title_data in titles:
                        title, created = Title.objects.get_or_create(
                            name=title_data['name'],
                            defaults=title_data
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created title: {title_data["name"]}'))
                        
                        # Добавляем титул "Создатель" админу если его еще нет
                        if title_data['name'] == 'Создатель' and not admin_user.profile.titles.filter(name='Создатель').exists():
                            admin_user.profile.titles.add(title)

                    self.stdout.write(self.style.SUCCESS('Successfully initialized all data'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error initializing data: {str(e)}'))

            finally:
                # Восстанавливаем сигналы
                from blog.signals import update_category_posts_count
                post_save.connect(update_category_posts_count, sender=Post)
 