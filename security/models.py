"""
Security models for LegacyGrid School Management System
"""
import uuid
import hashlib
import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class LicenseKey(models.Model):
    """
    License management for anti-cloning protection
    """
    key = models.CharField(max_length=255, unique=True)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='licenses')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_validated = models.DateTimeField(null=True, blank=True)
    validation_signature = models.CharField(max_length=512, blank=True)
    
    class Meta:
        verbose_name = "License Key"
        verbose_name_plural = "License Keys"
    
    def __str__(self):
        return f"License for {self.school.name}"
    
    def generate_key(self):
        """Generate a unique license key"""
        unique_str = f"{self.school.id}-{self.owner.username}-{timezone.now().isoformat()}"
        self.key = hashlib.sha256(unique_str.encode()).hexdigest()[:32].upper()
        return self.key
    
    def validate_signature(self, signature):
        """Validate license signature"""
        expected = self.generate_validation_signature()
        return signature == expected
    
    def generate_validation_signature(self):
        """Generate validation signature"""
        data = f"{self.key}-{self.school.id}-{settings.SECRET_KEY}"
        return hashlib.sha256(data.encode()).hexdigest()


class EnvironmentFingerprint(models.Model):
    """
    Environment fingerprinting for clone detection
    """
    school = models.OneToOneField('schools.School', on_delete=models.CASCADE)
    fingerprint_hash = models.CharField(max_length=128, unique=True)
    server_signature = models.TextField()
    environment_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    last_verified = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Environment Fingerprint"
        verbose_name_plural = "Environment Fingerprints"
    
    def __str__(self):
        return f"Fingerprint for {self.school.name}"
    
    def generate_fingerprint(self, request=None):
        """Generate environment fingerprint"""
        import platform
        import socket
        
        # Collect environment data
        env_data = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'hostname': socket.gethostname(),
            'django_version': getattr(settings, 'DJANGO_VERSION', ''),
        }
        
        if request:
            env_data.update({
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'remote_addr': request.META.get('REMOTE_ADDR', ''),
                'server_name': request.META.get('SERVER_NAME', ''),
            })
        
        self.environment_data = env_data
        
        # Generate hash
        data_str = json.dumps(env_data, sort_keys=True)
        self.fingerprint_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        return self.fingerprint_hash


class AuditLog(models.Model):
    """
    Audit logging for compliance and security monitoring
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log Entries"
        ordering = ['-timestamp']
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{user_str} - {self.method} {self.path} [{self.status_code}]"


class SecurityEvent(models.Model):
    """
    Security events and threats monitoring
    """
    EVENT_TYPES = [
        ('LOGIN_FAILED', 'Failed Login Attempt'),
        ('ADMIN_ACCESS_DENIED', 'Admin Access Denied'),
        ('GEO_BLOCKED', 'Geographic Access Blocked'),
        ('RATE_LIMIT_EXCEEDED', 'Rate Limit Exceeded'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity Detected'),
        ('CLONE_DETECTED', 'Potential Clone Detected'),
        ('LICENSE_VIOLATION', 'License Violation'),
        ('HTTP_ERROR', 'HTTP Error'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access Attempt'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    description = models.TextField()
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    severity = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ], default='MEDIUM')
    
    class Meta:
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.ip_address} [{self.severity}]"


class IPWhitelist(models.Model):
    """
    IP Whitelisting for admin access
    """
    ip_address = models.GenericIPAddressField(unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "IP Whitelist Entry"
        verbose_name_plural = "IP Whitelist Entries"
    
    def __str__(self):
        return f"{self.ip_address} - {self.description}"


class TwoFactorBackupCode(models.Model):
    """
    Backup codes for 2FA recovery
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backup_codes')
    code = models.CharField(max_length=16)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "2FA Backup Code"
        verbose_name_plural = "2FA Backup Codes"
        unique_together = ['user', 'code']
    
    def __str__(self):
        return f"Backup code for {self.user.username}"


class PasswordHistory(models.Model):
    """
    Password history tracking for security policies
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Password History"
        verbose_name_plural = "Password History"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Password history for {self.user.username} - {self.created_at}"
