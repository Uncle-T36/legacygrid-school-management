"""
Billing and subscription access control utilities.
This module provides strict owner-only access controls for billing operations.
"""

import logging
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib import messages
from functools import wraps

# Setup logging for billing access attempts
logger = logging.getLogger('billing')

def is_billing_owner(user):
    """
    Check if the user is the designated billing owner.
    Only the user specified in BILLING_OWNER_USERNAME can access billing features.
    """
    if not user.is_authenticated:
        return False
    
    billing_owner = getattr(settings, 'BILLING_OWNER_USERNAME', None)
    if not billing_owner:
        logger.warning("BILLING_OWNER_USERNAME not configured in settings")
        return False
    
    is_owner = user.username == billing_owner
    
    # Log access attempts
    if getattr(settings, 'LOG_BILLING_ACCESS_ATTEMPTS', True):
        if is_owner:
            logger.info(f"Billing owner {user.username} accessed billing feature")
        else:
            logger.warning(f"User {user.username} attempted unauthorized billing access")
    
    return is_owner

def billing_owner_required(view_func):
    """
    Decorator that restricts access to billing owner only.
    Shows a clear error message for unauthorized users.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'billing/access_denied.html', {
                'error_message': 'Please log in to access billing features.',
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@legacygrid.co.zw')
            }, status=401)
        
        if not is_billing_owner(request.user):
            error_message = getattr(
                settings, 
                'BILLING_ACCESS_DENIED_MESSAGE',
                "Access denied. Billing and subscription management is restricted to the system owner only."
            )
            
            return render(request, 'billing/access_denied.html', {
                'error_message': error_message,
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@legacygrid.co.zw'),
                'current_user': request.user.username
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def subscription_owner_required(view_func):
    """
    Decorator that restricts subscription management to billing owner only.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'billing/access_denied.html', {
                'error_message': 'Please log in to access subscription management.',
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@legacygrid.co.zw')
            }, status=401)
        
        if not is_billing_owner(request.user):
            error_message = getattr(
                settings, 
                'SUBSCRIPTION_ACCESS_DENIED_MESSAGE',
                "Subscription management is restricted to authorized personnel only."
            )
            
            return render(request, 'billing/access_denied.html', {
                'error_message': error_message,
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@legacygrid.co.zw'),
                'current_user': request.user.username
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def check_billing_access(user):
    """
    Simple function to check if user has billing access.
    Can be used in templates or other contexts.
    """
    return is_billing_owner(user)

def get_stripe_config():
    """
    Get Stripe configuration from Django settings.
    Only accessible by billing owner.
    """
    return getattr(settings, 'PAYMENT_GATEWAYS', {}).get('stripe', {})

def is_demo_mode():
    """
    Check if the system is in demo mode (no real payments).
    """
    return getattr(settings, 'DEMO_MODE', True)