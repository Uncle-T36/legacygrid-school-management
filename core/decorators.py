from functools import wraps
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .models import TenantFeatureToggle, FeatureToggle
from .middleware import get_current_tenant

def owner_only(view_func):
    """
    Enhanced decorator that restricts access to only the owner (Uncle-T36).
    Redirects unauthorized users to the 'not_authorized' page.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.username == settings.BILLING_OWNER_USERNAME:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('not_authorized')
    return _wrapped_view


def owner_or_admin(view_func):
    """
    Decorator that allows access to owner or users with admin permissions.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if (request.user.username == settings.BILLING_OWNER_USERNAME or 
            request.user.is_superuser or 
            request.user.groups.filter(name='Admin').exists()):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('not_authorized')
    return _wrapped_view


def requires_feature(feature_name):
    """
    Decorator that checks if a feature is enabled for the current tenant.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            tenant = get_current_tenant()
            
            if not tenant:
                # No tenant context, check global feature toggle
                try:
                    feature = FeatureToggle.objects.get(name=feature_name)
                    if not feature.is_enabled_globally:
                        raise PermissionDenied("Feature not available")
                except FeatureToggle.DoesNotExist:
                    raise PermissionDenied("Feature not found")
            else:
                # Check tenant-specific feature toggle
                try:
                    tenant_feature = TenantFeatureToggle.objects.get(
                        tenant=tenant, 
                        feature__name=feature_name,
                        is_enabled=True
                    )
                except TenantFeatureToggle.DoesNotExist:
                    # Check if feature is globally enabled
                    try:
                        feature = FeatureToggle.objects.get(
                            name=feature_name,
                            is_global=True,
                            is_enabled_globally=True
                        )
                    except FeatureToggle.DoesNotExist:
                        raise PermissionDenied("Feature not available for this tenant")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def requires_subscription(tier):
    """
    Decorator that checks if the user/tenant has the required subscription tier.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            tenant = get_current_tenant()
            
            # Owner always has access
            if request.user.username == settings.BILLING_OWNER_USERNAME:
                return view_func(request, *args, **kwargs)
            
            if not tenant:
                raise PermissionDenied("No tenant context")
            
            # Check subscription tier
            required_tier_priority = get_tier_priority(tier)
            current_tier_priority = get_tier_priority(tenant.subscription_tier)
            
            if current_tier_priority < required_tier_priority:
                if request.is_ajax():
                    return JsonResponse({
                        'error': 'Subscription upgrade required',
                        'required_tier': tier,
                        'current_tier': tenant.subscription_tier
                    }, status=403)
                else:
                    return redirect('billing:upgrade_required')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def api_key_required(view_func):
    """
    Decorator for API views that require API key authentication.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        api_key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        
        if not api_key:
            return JsonResponse({'error': 'API key required'}, status=401)
        
        # Validate API key (implement your validation logic)
        if not validate_api_key(api_key, request):
            return JsonResponse({'error': 'Invalid API key'}, status=401)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def audit_action(action_type):
    """
    Decorator to automatically log actions for audit purposes.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Execute the view
            response = view_func(request, *args, **kwargs)
            
            # Log the action after successful execution
            if hasattr(request, 'user') and request.user.is_authenticated:
                from .models import AuditLog
                try:
                    AuditLog.objects.create(
                        user=request.user,
                        tenant=get_current_tenant(),
                        action=action_type,
                        resource=request.path,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        notes=f"View: {view_func.__name__}"
                    )
                except Exception:
                    # Don't break the view if logging fails
                    pass
            
            return response
        return _wrapped_view
    return decorator


def get_tier_priority(tier_name):
    """
    Get the priority level of a subscription tier.
    Higher number = higher tier.
    """
    tier_priorities = {
        'free': 0,
        'starter': 1,
        'professional': 2,
        'enterprise': 3,
    }
    return tier_priorities.get(tier_name, 0)


def validate_api_key(api_key, request):
    """
    Validate API key for API access.
    This is a placeholder - implement your actual validation logic.
    """
    # TODO: Implement actual API key validation
    # This could check against a database of valid API keys
    # associated with tenants or users
    return True  # Placeholder


def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip