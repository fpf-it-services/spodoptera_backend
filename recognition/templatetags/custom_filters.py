from django import template

register = template.Library()


@register.filter
def divide(value, arg):
    try:
        return (value / arg * 100) if arg else 0
    except (ZeroDivisionError, TypeError):
        return 0
