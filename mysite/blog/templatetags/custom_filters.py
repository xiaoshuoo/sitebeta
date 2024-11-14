from django import template
import random

register = template.Library()

@register.filter
def random_int(value, args):
    try:
        min_val, max_val = map(int, args.split(':'))
        return random.randint(min_val, max_val)
    except (ValueError, AttributeError):
        return 0

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 