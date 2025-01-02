from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from blog.models import Post, Category, Tag
from django.utils.html import escape
from django.urls import reverse

def search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    
    if not query or len(query) < 2:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'results': []})
        return JsonResponse({'results': []})
    
    results = []
    
    if search_type in ['all', 'posts']:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct().order_by('-created_at')[:5]
        
        for post in posts:
            # Находим контекст для подсветки
            content = post.content
            start_idx = content.lower().find(query.lower())
            if start_idx != -1:
                start = max(0, start_idx - 50)
                end = min(len(content), start_idx + len(query) + 50)
                highlight = '...' + escape(content[start:end]) + '...'
            else:
                highlight = escape(content[:100]) + '...'

            results.append({
                'type': 'post',
                'icon': 'fa-file-alt',
                'title': escape(post.title),
                'url': reverse('blog:post_detail', kwargs={'slug': post.slug}),
                'subtitle': f'В категории {escape(post.category.name)}',
                'highlight': highlight
            })
    
    if search_type in ['all', 'categories']:
        categories = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()[:3]
        
        for category in categories:
            post_count = category.posts.count()
            results.append({
                'type': 'category',
                'icon': 'fa-folder',
                'title': escape(category.name),
                'url': reverse('blog:category_detail', kwargs={'slug': category.slug}),
                'subtitle': f'{post_count} {post_count % 10 == 1 and post_count % 100 != 11 and "пост" or "постов"}',
                'highlight': escape(category.description[:100]) if category.description else ''
            })
    
    if search_type in ['all', 'tags']:
        tags = Tag.objects.filter(name__icontains=query).distinct()[:5]
        for tag in tags:
            post_count = tag.posts.count()
            results.append({
                'type': 'tag',
                'icon': 'fa-tag',
                'title': escape(tag.name),
                'url': reverse('blog:tag_detail', kwargs={'slug': tag.slug}),
                'subtitle': f'{post_count} {post_count % 10 == 1 and post_count % 100 != 11 and "пост" or "постов"}',
                'highlight': ''
            })

    # Возвращаем JSON для AJAX-запросов
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'results': results,
            'query': query,
            'total': len(results)
        })
    
    # Для обычных запросов возвращаем JSON (так как фронтенд всё равно ожидает JSON)
    return JsonResponse({
        'results': results,
        'query': query,
        'total': len(results)
    }) 