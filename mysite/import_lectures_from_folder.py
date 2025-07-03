import os
import django
from django.utils.text import slugify
import uuid

# pip install transliterate
try:
    from transliterate import translit
except ImportError:
    translit = None

# Установить настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import Lecture, Category

CATEGORIES = [
    {"name": "Заболевания", "slug": "zabolevaniya", "icon": "fas fa-notes-medical", "keywords": ["болезнь", "zabolevanie", "заболевание", "bolezn", "инфекция", "infekciya", "грипп", "gripp", "ОРВИ", "orvi", "рак", "rak", "СПИД", "spid", "ВИЧ", "vich", "инфаркт", "infarkt", "инсульт", "insult"]},
    {"name": "Первая помощь", "slug": "pervaya-pomosh", "icon": "fas fa-first-aid", "keywords": ["ПМП", "pmp", "первая помощь", "pervaya pomosh", "pp", "пп", "помощь", "pomosh"]},
    {"name": "Другое", "slug": "drugoe", "icon": "fas fa-book-medical", "keywords": []},  # Пустой список, т.к. это категория по умолчанию
    {"name": "Для МВД", "slug": "dlya-mvd", "icon": "fas fa-shield-alt", "keywords": ["МВД", "mvd", "полиция", "policiya", "полицейский", "policeyskiy", "спорт", "sport", "физическая подготовка", "fizicheskaya podgotovka"]}
]

def import_lectures_from_folder(folder_path):
    """
    Импортирует лекции из указанной папки
    """
    # Создаем категории, если их нет
    for category_data in CATEGORIES:
        Category.objects.get_or_create(
            slug=category_data["slug"],
            defaults={
                "name": category_data["name"],
                "icon": category_data["icon"]
            }
        )

    # Получаем все категории
    categories = {c.slug: c for c in Category.objects.all()}
    
    # Получаем список файлов
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]
    
    # Счетчики
    imported_count = 0
    error_count = 0
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        try:
            # Просто читаем файл как UTF-8, без попыток перекодировки
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().replace('\x00', '')
            
            print(f'=== Файл: {filename} ===')
            print(f'Первые 200 символов: {content[:200]}')
            print('=== Конец вывода ===')
            
            title = os.path.splitext(filename)[0]
            
            # Определяем категорию на основе имени файла и содержимого
            category = determine_category(title, content)
            
            print(f'--- TO DB: {title} ---')
            print(content[:500])
            print('--- END TO DB ---')
            
            # Создаем или обновляем лекцию
            lecture, created = Lecture.objects.update_or_create(
                title=title,
                defaults={
                    'content': content,
                    'category': category,
                    'slug': slugify(title) if not translit else slugify(translit(title, 'ru', reversed=True))
                }
            )
            
            print(f'Импортировано: {title} (категория: {category.name})')
            imported_count += 1
            
        except Exception as e:
            print(f'Ошибка при импорте {filename}: {str(e)}')
            error_count += 1
    
    print(f'Успешно импортировано: {imported_count}, ошибок: {error_count}')

def determine_category(title, content):
    """
    Определяет категорию лекции на основе ключевых слов в названии и содержимом
    """
    # Сначала проверяем название на ключевые слова "Первая помощь" (приоритет)
    title_lower = title.lower()
    for keyword in CATEGORIES[1]["keywords"]:  # Первая помощь
        if keyword.lower() in title_lower:
            return Category.objects.get(slug=CATEGORIES[1]["slug"])
    
    # Затем проверяем содержимое на все категории
    content_lower = content.lower()
    
    # Проверяем каждую категорию по порядку приоритета
    for category_data in CATEGORIES:
        for keyword in category_data["keywords"]:
            if keyword.lower() in title_lower or keyword.lower() in content_lower:
                return Category.objects.get(slug=category_data["slug"])
    
    # Если ничего не нашли, возвращаем "Другое"
    return Category.objects.get(slug=CATEGORIES[2]["slug"])

if __name__ == "__main__":
    # Удаляем все старые лекции перед импортом
    from blog.models import Lecture
    deleted, _ = Lecture.objects.all().delete()
    print(f'Удалено старых лекций: {deleted}')
    
    # Определяем папку для импорта
    import sys
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = "utf8_fixed"  # По умолчанию
    
    print(f'Импорт лекций из папки: {folder_path}')
    import_lectures_from_folder(folder_path) 