from functools import wraps
from django.http import HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def owner_only_billing(view_func):
    """
    Decorator to restrict billing access to owner only (Uncle-T36)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not settings.ALLOW_ONLY_OWNER_BILLING:
            return view_func(request, *args, **kwargs)
        
        if request.user.username != settings.BILLING_OWNER_USERNAME and not request.user.is_superuser:
            messages.error(request, "Access denied. Only the billing owner can access this section.")
            return redirect('admin:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def subscription_required(feature_name=None, tier_required=None):
    """
    Decorator to check if user has required subscription tier or feature access
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Get user subscription
            from .models import UserSubscription
            try:
                subscription = UserSubscription.objects.get(user=request.user)
            except UserSubscription.DoesNotExist:
                subscription = None
            
            # Check tier requirement
            if tier_required:
                if not subscription or subscription.tier.name != tier_required:
                    messages.error(request, f"This feature requires {tier_required} subscription.")
                    return redirect('billing:upgrade')
            
            # Check feature requirement
            if feature_name:
                if not subscription or not subscription.has_feature(feature_name):
                    messages.error(request, f"This feature requires a subscription with {feature_name} access.")
                    return redirect('billing:upgrade')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def premium_required(view_func):
    """
    Shortcut decorator for premium subscription requirement
    """
    return subscription_required(tier_required='premium')(view_func)


def ai_access_required(view_func):
    """
    Decorator to check if user has AI access
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        from .models import UserSubscription
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            if not subscription.tier.ai_access:
                messages.error(request, "AI features require a premium subscription.")
                return redirect('billing:upgrade')
        except UserSubscription.DoesNotExist:
            messages.error(request, "AI features require a subscription.")
            return redirect('billing:upgrade')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def demo_mode_check(view_func):
    """
    Decorator to handle demo mode restrictions
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if settings.DEMO_MODE:
            messages.warning(request, "Demo mode is active. No real payments will be processed.")
        
        return view_func(request, *args, **kwargs)
    return wrapper