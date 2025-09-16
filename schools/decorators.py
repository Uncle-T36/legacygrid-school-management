"""
Access control decorators for the LegacyGrid School Management System.
Implements strict owner-only access controls for billing and subscription management.
"""

from functools import wraps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template.response import TemplateResponse


def owner_required(view_func=None, *, unauthorized_template=None, redirect_to=None):
    """
    Decorator that ensures only the system owner (Uncle-T36) can access a view.
    
    Args:
        view_func: The view function to wrap
        unauthorized_template: Custom template to render for unauthorized users
        redirect_to: URL to redirect unauthorized users to
    
    Returns:
        Decorated view function that checks for owner access
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Check if billing access control is enabled
            billing_config = getattr(settings, 'BILLING_ACCESS_CONTROL', {})
            
            if not billing_config.get('enabled', False):
                # If access control is disabled, allow all authenticated users
                return view_func(request, *args, **kwargs)
            
            # Check if user is the system owner
            owner_username = billing_config.get('owner_username', settings.BILLING_OWNER_USERNAME)
            
            if request.user.username != owner_username:
                # User is not the owner - deny access
                unauthorized_msg = billing_config.get(
                    'unauthorized_message',
                    'Access Denied: Only the system owner can access this feature.'
                )
                
                messages.error(request, unauthorized_msg)
                
                # Handle redirect or template rendering
                if unauthorized_template:
                    return TemplateResponse(
                        request,
                        unauthorized_template,
                        {'error_message': unauthorized_msg}
                    )
                elif redirect_to:
                    return redirect(redirect_to)
                else:
                    # Use configured redirect URL or default
                    redirect_url = billing_config.get('redirect_url', '/schools/profile/')
                    return redirect(redirect_url)
            
            # User is the owner - allow access
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)


def billing_access_required(view_func):
    """
    Specific decorator for billing-related views.
    Only allows the system owner to access billing functionality.
    """
    return owner_required(
        view_func,
        unauthorized_template='schools/billing_unauthorized.html',
        redirect_to='/schools/profile/'
    )


def is_system_owner(user):
    """
    Check if the given user is the system owner.
    
    Args:
        user: Django User object
        
    Returns:
        bool: True if user is the system owner, False otherwise
    """
    if not user.is_authenticated:
        return False
    
    billing_config = getattr(settings, 'BILLING_ACCESS_CONTROL', {})
    owner_username = billing_config.get('owner_username', settings.BILLING_OWNER_USERNAME)
    
    return user.username == owner_username


def get_billing_access_message():
    """
    Get the configured unauthorized access message for billing.
    
    Returns:
        str: The configured unauthorized message
    """
    billing_config = getattr(settings, 'BILLING_ACCESS_CONTROL', {})
    return billing_config.get(
        'unauthorized_message',
        'Access Denied: Only the system owner can access billing and subscription management.'
    )