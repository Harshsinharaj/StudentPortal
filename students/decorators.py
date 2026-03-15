from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    """Decorator to check if user is admin/superuser"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return wrapper

def require_admin(view_func):
    """Alternative admin check using user_passes_test"""
    return user_passes_test(lambda u: u.is_superuser or u.is_staff)(view_func)
