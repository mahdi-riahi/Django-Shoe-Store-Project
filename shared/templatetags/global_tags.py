from django import template

register = template.Library()

@register.filter
def multiply(value1, value2):
    return value1 * value2


@register.filter
def active_objects(objects):
    return objects.filter(is_active=True)
