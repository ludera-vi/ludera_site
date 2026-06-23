from django import template

register = template.Library()


@register.filter
def field(obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr, '')
    return obj.__dict__.get(attr, '')


@register.filter
def can_access(user, section):
    if user.is_superuser:
        return True
    return user.cabinet_permissions.filter(section=section).exists()



