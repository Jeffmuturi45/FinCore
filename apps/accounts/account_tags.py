from django import template

register = template.Library()


@register.filter
def has_role(user, role_slug):
    """Usage: {% if request.user|has_role:"loan-officer" %}"""
    return user.is_authenticated and user.has_role(role_slug)


@register.simple_tag(takes_context=True)
def user_role_name(context):
    user = context.get("user") or context["request"].user
    if user.is_superuser:
        return "Super Admin"
    if user.role:
        return user.role.name
    return "No Role"


@register.filter
def is_super_admin(user):
    return user.is_authenticated and user.is_super_admin()


@register.filter
def is_staff_member(user):
    return user.is_authenticated and user.is_staff_member()
