"""
Security middleware for LegacyGrid School Management System
Implements advanced security features like IP whitelisting, geo-blocking, and audit logging.
"""
import json
import logging
import time
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog, SecurityEvent
from .utils import get_client_ip, get_country_from_ip, detect_suspicious_activity

logger = logging.getLogger('security')


class SecurityMiddleware(MiddlewareMixin):
    """
    Advanced security middleware implementing:
    - IP whitelisting for admin areas
    - Geo-blocking
    - Audit logging
    - Suspicious activity detection
    """
    
    def process_request(self, request):
        """Process incoming requests for security checks."""
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Store security context
        request.security_context = {
            'ip': client_ip,
            'user_agent': user_agent,
            'timestamp': time.time(),
            'path': request.path,
            'method': request.method,
        }
        
        # IP Whitelisting for admin areas
        if request.path.startswith('/admin/') and hasattr(settings, 'ADMIN_IP_WHITELIST'):
            if settings.ADMIN_IP_WHITELIST and client_ip not in settings.ADMIN_IP_WHITELIST:
                logger.warning(f"Admin access denied for IP {client_ip}")
                self.log_security_event(request, 'ADMIN_ACCESS_DENIED', 'IP not whitelisted')
                return HttpResponseForbidden("Access denied: IP not authorized for admin access")
        
        # Geo-blocking
        if getattr(settings, 'GEO_BLOCKING_ENABLED', False):
            country = get_country_from_ip(client_ip)
            allowed_countries = getattr(settings, 'ALLOWED_COUNTRIES', [])
            if country and allowed_countries and country not in allowed_countries:
                logger.warning(f"Access denied for country {country} from IP {client_ip}")
                self.log_security_event(request, 'GEO_BLOCKED', f'Country: {country}')
                return HttpResponseForbidden("Access denied: Geographic location not authorized")
        
        # Rate limiting check (basic implementation)
        if self.check_rate_limit(request, client_ip):
            logger.warning(f"Rate limit exceeded for IP {client_ip}")
            self.log_security_event(request, 'RATE_LIMIT_EXCEEDED', 'Too many requests')
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
        
        return None
    
    def process_response(self, request, response):
        """Process responses for audit logging."""
        if hasattr(request, 'security_context') and hasattr(request, 'user'):
            # Log successful requests
            if response.status_code < 400:
                self.log_audit_event(request, response)
            else:
                # Log failed requests as security events
                self.log_security_event(request, 'HTTP_ERROR', f'Status: {response.status_code}')
        
        return response
    
    def log_audit_event(self, request, response):
        """Log audit events for compliance and monitoring."""
        try:
            user = request.user if request.user.is_authenticated else None
            AuditLog.objects.create(
                user=user,
                ip_address=request.security_context['ip'],
                user_agent=request.security_context['user_agent'],
                path=request.security_context['path'],
                method=request.security_context['method'],
                status_code=response.status_code,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    def log_security_event(self, request, event_type, description):
        """Log security events for threat monitoring."""
        try:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            SecurityEvent.objects.create(
                user=user,
                ip_address=request.security_context.get('ip', ''),
                event_type=event_type,
                description=description,
                user_agent=request.security_context.get('user_agent', ''),
                path=request.security_context.get('path', ''),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def check_rate_limit(self, request, client_ip):
        """Basic rate limiting implementation."""
        if not getattr(settings, 'RATELIMIT_ENABLE', False):
            return False
        
        # Rate limit key
        key = f"rate_limit:{client_ip}"
        
        # Get current count
        current_count = cache.get(key, 0)
        
        # Define limits (can be made configurable)
        limit_per_minute = 60
        
        if current_count >= limit_per_minute:
            return True
        
        # Increment counter
        cache.set(key, current_count + 1, 60)  # 60 seconds window
        
        return False