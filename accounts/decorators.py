from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Require authentication and one of the application's roles."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            # Keamanan: guard hasattr untuk mencegah AttributeError
            # jika user tidak memiliki atribut 'role' (mis. AnonymousUser)
            if not hasattr(request.user, 'role') or request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
