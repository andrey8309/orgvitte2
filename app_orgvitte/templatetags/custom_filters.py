from django import template

register = template.Library()

@register.filter
def pluck(queryset, key):
    """
    Использование: {{ queryset|pluck:"field" }}
    Превращает queryset вида [{'field': 'A', 'total': 10}, ...]
    в список ['A', ...] или [10, ...]
    """
    return [getattr(obj, key, None) if not isinstance(obj, dict) else obj.get(key) for obj in queryset]
