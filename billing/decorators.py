from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import render
from functools import wraps


def is_owner(user):
    """Check if user is the owner (Uncle-T36)"""
    return user.is_authenticated and user.username == settings.OWNER_USERNAME


def owner_required(view_func):
    """Decorator that restricts access to owner only"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'billing/access_denied.html', {
                'message': 'Please log in as the owner to access billing features.',
                'login_required': True
            }, status=401)
        
        if not is_owner(request.user):
            return render(request, 'billing/access_denied.html', {
                'message': 'Access denied. Only Uncle-T36 (system owner) can access billing features.',
                'current_user': request.user.username
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def owner_only_test(user):
    """Test function for user_passes_test decorator"""
    return is_owner(user)


# Use this decorator for class-based views
owner_required_cbv = user_passes_test(owner_only_test, login_url='/admin/login/')