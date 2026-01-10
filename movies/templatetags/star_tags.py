from django import template

register = template.Library()

@register.filter
def stars(value):
    try:
        value = float(value)
    except:
        return ""
    full = int(value)
    half = 1 if value - full >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "½" * half + "☆" * empty
