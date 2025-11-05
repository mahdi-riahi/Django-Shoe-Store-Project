from django import template

register = template.Library()

@register.filter
def active_objects(objects):
    return objects.filter(is_active=True)
