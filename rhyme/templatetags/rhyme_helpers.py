from django import template

register = template.Library()

@register.filter
def int_range(i):
    return range(int(i or 0))
