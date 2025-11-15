from django import template

from products.models import Product


register = template.Library()

@register.filter
def dict_first_three_elements(dictionary):
    if len(dictionary) > 3:
        return dict(list(dictionary.items())[:3])
    return dictionary

@register.filter
def turn_number_to_letter(value):
    string_numbers = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    return string_numbers[int(value)]

@register.filter
def find_category_from_category_display_product(display):
    for group_name, subgroups in Product.CATEGORIES:
        for value, label in subgroups:
            if label == display:
                return value
    return None
