from django import template
from django.forms.widgets import CheckboxInput

register = template.Library()

@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)

@register.filter
def add_classes(field, classes):
    return field.as_widget(attrs={"class": classes})

@register.filter
def field_type(field):
    return field.field.widget.__class__.__name__