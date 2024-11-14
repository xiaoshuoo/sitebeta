from django import template
import random

register = template.Library()

@register.simple_tag
def random_position():
    """Возвращает случайное число от 0 до 100 для позиционирования элементов"""
    return random.randint(0, 100)

@register.filter
def multiply(value, arg):
    """Умножает value на arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def random_int(value, max_value):
    """Возвращает случайное число от value до max_value"""
    try:
        return random.randint(int(value), int(max_value))
    except (ValueError, TypeError):
        return value