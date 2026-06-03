from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps
from .models import User


def role_required(*allowed_roles):
    """
    Decorator to check if user has any of the allowed roles.
    Usage: @role_required('super_admin', 'admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            # Superusers have access to everything
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if user has any of the allowed roles
            for role_slug in allowed_roles:
                # Fixed: only pass role_slug
                if request.user.has_role(role_slug):
                    return view_func(request, *args, **kwargs)

            # No permission
            raise PermissionDenied(
                "You don't have permission to access this page.")

        return wrapper
    return decorator
