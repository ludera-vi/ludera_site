from django import template

register = template.Library()


@register.filter
def field(obj, attr):
    parts = attr.split('.')
    val = obj
    for part in parts:
        if hasattr(val, part):
            val = getattr(val, part, '')
        elif isinstance(val, dict):
            val = val.get(part, '')
        else:
            return ''
    if callable(val):
        try:
            val = val()
        except TypeError:
            return ''
    return val if val is not None else ''


@register.filter
def can_access(user, section):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.cabinet_permissions.filter(section=section).exists()



