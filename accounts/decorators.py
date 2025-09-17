from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import AuditLog


def role_required(allowed_roles):
    """Decorator to restrict access based on user roles"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'You do not have permission to access this page.')
            return HttpResponseForbidden('Access denied')
        
        return _wrapped_view
    return decorator


def permission_required(permission):
    """Decorator to check specific permissions"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.has_permission(permission):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, f'You do not have the "{permission}" permission.')
            return HttpResponseForbidden('Access denied')
        
        return _wrapped_view
    return decorator


def audit_action(action_name):
    """Decorator to log user actions"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not getattr(settings, 'AUDIT_LOG_ENABLED', False):
                return view_func(request, *args, **kwargs)
            
            # Execute the view first
            response = view_func(request, *args, **kwargs)
            
            # Log the action after successful execution
            if request.user.is_authenticated and hasattr(request, 'user'):
                try:
                    # Get client IP
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip_address = x_forwarded_for.split(',')[0]
                    else:
                        ip_address = request.META.get('REMOTE_ADDR')
                    
                    AuditLog.objects.create(
                        user=request.user,
                        action=action_name,
                        ip_address=ip_address,
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        changes={'url': request.path, 'method': request.method}
                    )
                except Exception:
                    # Don't let audit logging break the view
                    pass
            
            return response
        
        return _wrapped_view
    return decorator


def owner_or_school_admin(view_func):
    """Decorator to allow access to owners or school admins only"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if (request.user.is_superuser or 
            request.user.role == 'owner' or 
            (request.user.role == 'admin' and request.user.school)):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'You must be a school administrator to access this page.')
        return HttpResponseForbidden('Access denied')
    
    return _wrapped_view


def same_school_required(view_func):
    """Decorator to ensure user can only access data from their school"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Owners can access all schools
        if request.user.is_superuser or request.user.role == 'owner':
            return view_func(request, *args, **kwargs)
        
        # Others must have a school assigned
        if not request.user.school:
            messages.error(request, 'You must be assigned to a school to access this page.')
            return HttpResponseForbidden('Access denied')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


class RoleBasedAccessMixin:
    """Mixin for class-based views to handle role-based access"""
    allowed_roles = []
    required_permission = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check roles
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            if not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access this page.')
                return HttpResponseForbidden('Access denied')
        
        # Check specific permission
        if self.required_permission and not request.user.has_permission(self.required_permission):
            messages.error(request, f'You do not have the "{self.required_permission}" permission.')
            return HttpResponseForbidden('Access denied')
        
        return super().dispatch(request, *args, **kwargs)