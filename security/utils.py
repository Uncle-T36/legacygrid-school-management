"""
Security utilities for LegacyGrid School Management System
"""
import re
import json
import hashlib
import logging
import platform
import socket
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from .models import SecurityEvent, EnvironmentFingerprint

logger = logging.getLogger('security')


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_country_from_ip(ip_address):
    """
    Get country code from IP address.
    In production, you would use a service like MaxMind GeoIP2.
    This is a placeholder implementation.
    """
    # Placeholder implementation - in production use GeoIP2
    if ip_address.startswith('127.') or ip_address.startswith('192.168.'):
        return 'ZW'  # Local development
    return None


def detect_suspicious_activity(user, request):
    """
    Detect suspicious activity patterns.
    """
    if not user.is_authenticated:
        return False
    
    # Check for rapid requests from different IPs
    cache_key = f"user_ips:{user.id}"
    recent_ips = cache.get(cache_key, [])
    current_ip = get_client_ip(request)
    
    if current_ip not in recent_ips:
        recent_ips.append(current_ip)
        cache.set(cache_key, recent_ips[-10:], 3600)  # Keep last 10 IPs for 1 hour
    
    # Alert if user has accessed from more than 5 different IPs in the last hour
    if len(recent_ips) > 5:
        log_security_event(
            user=user,
            ip_address=current_ip,
            event_type='SUSPICIOUS_ACTIVITY',
            description=f'User accessed from {len(recent_ips)} different IPs in the last hour',
            severity='HIGH'
        )
        return True
    
    return False


def log_security_event(user=None, ip_address='', event_type='', description='', severity='MEDIUM'):
    """
    Log a security event.
    """
    try:
        SecurityEvent.objects.create(
            user=user,
            ip_address=ip_address,
            event_type=event_type,
            description=description,
            severity=severity,
            timestamp=datetime.now()
        )
        logger.warning(f"Security Event: {event_type} - {description} [{ip_address}]")
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")


def generate_environment_fingerprint(school, request=None):
    """
    Generate environment fingerprint for clone detection.
    """
    try:
        fingerprint, created = EnvironmentFingerprint.objects.get_or_create(school=school)
        if created or not fingerprint.is_verified:
            fingerprint.generate_fingerprint(request)
            fingerprint.save()
        return fingerprint
    except Exception as e:
        logger.error(f"Failed to generate environment fingerprint: {e}")
        return None


def validate_license_key(school, key):
    """
    Validate license key for anti-cloning protection.
    """
    try:
        from .models import LicenseKey
        license_obj = LicenseKey.objects.filter(school=school, key=key, is_active=True).first()
        
        if not license_obj:
            log_security_event(
                event_type='LICENSE_VIOLATION',
                description=f'Invalid license key attempted for school {school.name}',
                severity='HIGH'
            )
            return False
        
        # Check expiration
        if license_obj.expires_at and license_obj.expires_at < timezone.now():
            log_security_event(
                user=license_obj.owner,
                event_type='LICENSE_VIOLATION',
                description=f'Expired license key used for school {school.name}',
                severity='HIGH'
            )
            return False
        
        # Update last validation time
        license_obj.last_validated = timezone.now()
        license_obj.save()
        
        return True
    except Exception as e:
        logger.error(f"License validation error: {e}")
        return False


def check_clone_detection(school, request):
    """
    Check for potential cloning by comparing environment fingerprints.
    """
    try:
        fingerprint = EnvironmentFingerprint.objects.filter(school=school).first()
        if not fingerprint:
            return False
        
        # Generate current environment data
        current_env = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'hostname': socket.gethostname(),
        }
        
        if request:
            current_env.update({
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'remote_addr': request.META.get('REMOTE_ADDR', ''),
                'server_name': request.META.get('SERVER_NAME', ''),
            })
        
        # Compare with stored fingerprint
        stored_env = fingerprint.environment_data
        
        # Check for significant differences
        differences = []
        for key in ['platform', 'hostname']:
            if stored_env.get(key) != current_env.get(key):
                differences.append(key)
        
        # If significant differences found, flag as potential clone
        if differences:
            log_security_event(
                event_type='CLONE_DETECTED',
                description=f'Potential clone detected for school {school.name}. Differences: {differences}',
                ip_address=get_client_ip(request) if request else '',
                severity='CRITICAL'
            )
            return True
        
        return False
    except Exception as e:
        logger.error(f"Clone detection error: {e}")
        return False


def enforce_password_policy(password, user=None):
    """
    Enforce strong password policy.
    """
    errors = []
    
    # Length check
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long.")
    
    # Character requirements
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit.")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character.")
    
    # Common password check
    common_passwords = [
        'password', '123456', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890'
    ]
    if password.lower() in common_passwords:
        errors.append("Password is too common.")
    
    # User-specific checks
    if user:
        user_data = [user.username, user.first_name, user.last_name, user.email]
        for data in user_data:
            if data and data.lower() in password.lower():
                errors.append("Password cannot contain personal information.")
                break
    
    return errors


def generate_backup_codes(user, count=10):
    """
    Generate backup codes for 2FA recovery.
    """
    import secrets
    import string
    from .models import TwoFactorBackupCode
    
    codes = []
    alphabet = string.ascii_uppercase + string.digits
    
    # Clear existing unused codes
    TwoFactorBackupCode.objects.filter(user=user, is_used=False).delete()
    
    # Generate new codes
    for _ in range(count):
        code = ''.join(secrets.choice(alphabet) for _ in range(8))
        backup_code = TwoFactorBackupCode.objects.create(user=user, code=code)
        codes.append(code)
    
    return codes


def verify_backup_code(user, code):
    """
    Verify and consume a backup code.
    """
    from .models import TwoFactorBackupCode
    
    try:
        backup_code = TwoFactorBackupCode.objects.get(
            user=user, 
            code=code.upper(), 
            is_used=False
        )
        backup_code.is_used = True
        backup_code.used_at = datetime.now()
        backup_code.save()
        
        log_security_event(
            user=user,
            event_type='BACKUP_CODE_USED',
            description='2FA backup code used successfully',
            severity='MEDIUM'
        )
        
        return True
    except TwoFactorBackupCode.DoesNotExist:
        log_security_event(
            user=user,
            event_type='BACKUP_CODE_FAILED',
            description='Invalid 2FA backup code attempted',
            severity='HIGH'
        )
        return False


def obfuscate_sensitive_data(data):
    """
    Obfuscate sensitive data for logging.
    """
    if isinstance(data, str):
        if len(data) > 8:
            return data[:4] + '*' * (len(data) - 8) + data[-4:]
        else:
            return '*' * len(data)
    return str(data)


def watermark_response(response, school_name, owner_username):
    """
    Add watermark to responses for anti-cloning.
    """
    if hasattr(response, 'content') and b'</body>' in response.content:
        watermark = f'''
        <!-- LegacyGrid School Management System -->
        <!-- Licensed to: {school_name} -->
        <!-- Owner: {owner_username} -->
        <!-- Unauthorized duplication is prohibited -->
        <!-- Contact: support@legacygrid.co.zw -->
        '''
        response.content = response.content.replace(
            b'</body>',
            watermark.encode() + b'</body>'
        )
    return response