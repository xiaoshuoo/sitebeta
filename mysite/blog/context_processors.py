def admin_access(request):
    """
    Добавляет переменную show_admin_info в контекст шаблона
    """
    return {
        'show_admin_info': request.user.is_authenticated and 
                          (request.user.is_staff or request.user.is_superuser or 
                           getattr(request.user, 'is_admin', False))
    } 