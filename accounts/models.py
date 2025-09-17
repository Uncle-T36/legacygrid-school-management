from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class User(AbstractUser):
    """Extended User model with role-based access control"""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    preferred_language = models.CharField(max_length=5, default='en', choices=[
        ('en', 'English'),
        ('sn', 'Shona'),
        ('nd', 'Ndebele'),
    ])
    is_active_session = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    
    # School association - will be added in a separate migration
    # school = models.ForeignKey(
    #     'schools.School', 
    #     on_delete=models.CASCADE, 
    #     blank=True, 
    #     null=True,
    #     related_name='users'
    # )
    
    class Meta:
        db_table = 'accounts_user'
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.username
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        if self.role == 'owner' or self.is_superuser:
            return True
        
        role_perms = settings.USER_ROLES.get(self.role, {}).get('permissions', [])
        return permission in role_perms or 'all' in role_perms
    
    def get_role_level(self):
        """Get numeric role level for comparison"""
        return settings.USER_ROLES.get(self.role, {}).get('level', 0)
    
    def can_manage_user(self, other_user):
        """Check if current user can manage another user"""
        if self.role == 'owner' or self.is_superuser:
            return True
        return self.get_role_level() > other_user.get_role_level()
    
    def is_account_locked(self):
        """Check if account is temporarily locked due to failed attempts"""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def reset_failed_attempts(self):
        """Reset failed login attempts counter"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def increment_failed_attempts(self):
        """Increment failed login attempts and lock if necessary"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])


class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    notification_preferences = models.JSONField(default=dict, blank=True)
    theme_preference = models.CharField(max_length=10, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ])
    dashboard_layout = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"


class AuditLog(models.Model):
    """Audit log for tracking user actions"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"


class LoginHistory(models.Model):
    """Track user login history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        status = "Success" if self.success else f"Failed: {self.failure_reason}"
        return f"{self.user.username} - {status} - {self.login_time}"
