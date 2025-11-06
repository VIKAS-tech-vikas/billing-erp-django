from django import template

register = template.Library()

@register.filter
def sum(queryset, field_name):
    total = 0
    for obj in queryset:
        value = getattr(obj, field_name, 0)
        if value:
            total += value
    return total
