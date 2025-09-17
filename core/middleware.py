from django.http import Http404
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .models import Tenant, AuditLog
import threading

# Thread-local storage for current tenant
_thread_locals = threading.local()

class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant functionality.
    Determines the current tenant based on subdomain or domain.
    """
    
    def process_request(self, request):
        # Get host and determine tenant
        host = request.get_host()
        subdomain = None
        
        # Extract subdomain (basic implementation - can be enhanced)
        if '.' in host:
            parts = host.split('.')
            if len(parts) > 2:  # subdomain.domain.com
                subdomain = parts[0]
        
        # Try to find tenant by subdomain or domain
        tenant = None
        if subdomain:
            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        # Fallback to domain lookup
        if not tenant:
            try:
                tenant = Tenant.objects.get(domain=host, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        # Set tenant in request and thread-local storage
        request.tenant = tenant
        set_current_tenant(tenant)
        
        return None


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log user actions for audit purposes.
    Only logs actions for authenticated users and specific actions.
    """
    
    def process_response(self, request, response):
        # Only log for authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        # Skip certain paths and methods
        skip_paths = ['/static/', '/media/', '/favicon.ico']
        if any(request.path.startswith(path) for path in skip_paths):
            return response
        
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return response
        
        # Determine action type
        action = 'update'
        if request.method == 'POST':
            action = 'create'
        elif request.method == 'DELETE':
            action = 'delete'
        
        # Log the action
        try:
            AuditLog.objects.create(
                user=request.user,
                tenant=getattr(request, 'tenant', None),
                action=action,
                resource=request.path,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception:
            # Don't break the response if logging fails
            pass
        
        return response


def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_current_tenant():
    """Get the current tenant from thread-local storage."""
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage."""
    _thread_locals.tenant = tenant