from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Usage: {{ mydict|get_item:key }}"""
    return dictionary.get(key)

@register.filter
def split(value, separator):
    """Usage: {{ 'a,b,c'|split:',' }}"""
    return value.split(separator)