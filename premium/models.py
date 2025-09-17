"""
Premium features models for LegacyGrid School Management System
"""
import json
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class PremiumSubscription(models.Model):
    """
    Premium subscription management
    """
    TIERS = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    school = models.OneToOneField('schools.School', on_delete=models.CASCADE, related_name='subscription')
    tier = models.CharField(max_length=20, choices=TIERS, default='free')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    auto_renew = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Premium Subscription"
        verbose_name_plural = "Premium Subscriptions"
    
    def __str__(self):
        return f"{self.school.name} - {self.tier.title()}"
    
    def is_premium(self):
        return self.tier in ['premium', 'enterprise'] and self.is_active
    
    def has_feature(self, feature_name):
        """Check if subscription has access to a specific feature"""
        feature_gates = getattr(settings, 'FEATURE_GATES', {})
        required_tier = feature_gates.get(feature_name)
        
        if not required_tier:
            return True  # Feature is free
        
        tier_hierarchy = ['free', 'basic', 'premium', 'enterprise']
        current_index = tier_hierarchy.index(self.tier) if self.tier in tier_hierarchy else 0
        required_index = tier_hierarchy.index(required_tier) if required_tier in tier_hierarchy else 0
        
        return current_index >= required_index and self.is_active


class UsageAnalytics(models.Model):
    """
    Usage analytics and monitoring
    """
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='analytics')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    feature = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Usage Analytics"
        verbose_name_plural = "Usage Analytics"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['school', 'timestamp']),
            models.Index(fields=['feature', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.feature}:{self.action}"


class CustomDomain(models.Model):
    """
    Custom domain management for premium schools
    """
    school = models.OneToOneField('schools.School', on_delete=models.CASCADE, related_name='custom_domain')
    domain = models.CharField(max_length=255, unique=True)
    is_verified = models.BooleanField(default=False)
    ssl_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    dns_records = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Custom Domain"
        verbose_name_plural = "Custom Domains"
    
    def __str__(self):
        return f"{self.school.name} - {self.domain}"


class BackupConfiguration(models.Model):
    """
    Automated backup configuration
    """
    FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    school = models.OneToOneField('schools.School', on_delete=models.CASCADE, related_name='backup_config')
    is_enabled = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=FREQUENCIES, default='daily')
    retention_days = models.IntegerField(default=30)
    encryption_key = models.CharField(max_length=255, blank=True)
    last_backup = models.DateTimeField(null=True, blank=True)
    next_backup = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Backup Configuration"
        verbose_name_plural = "Backup Configurations"
    
    def __str__(self):
        return f"Backup config for {self.school.name}"


class BackupLog(models.Model):
    """
    Backup execution logs
    """
    STATUSES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='backup_logs')
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # in bytes
    file_path = models.CharField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Backup Log"
        verbose_name_plural = "Backup Logs"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Backup for {self.school.name} - {self.status}"


class FeedbackReport(models.Model):
    """
    Feedback and bug reports
    """
    TYPES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('feedback', 'General Feedback'),
        ('security', 'Security Issue'),
    ]
    
    PRIORITIES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUSES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='feedback_reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='medium')
    status = models.CharField(max_length=20, choices=STATUSES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)  # File paths
    
    class Meta:
        verbose_name = "Feedback Report"
        verbose_name_plural = "Feedback Reports"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type.title()}: {self.title}"


class UpdateConfiguration(models.Model):
    """
    Auto-update configuration (owner-controlled)
    """
    school = models.OneToOneField('schools.School', on_delete=models.CASCADE, related_name='update_config')
    auto_update_enabled = models.BooleanField(default=False)
    update_channel = models.CharField(max_length=20, choices=[
        ('stable', 'Stable'),
        ('beta', 'Beta'),
        ('alpha', 'Alpha'),
    ], default='stable')
    last_update_check = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)
    current_version = models.CharField(max_length=50, blank=True)
    maintenance_window = models.CharField(max_length=100, blank=True)  # e.g., "02:00-04:00"
    
    class Meta:
        verbose_name = "Update Configuration"
        verbose_name_plural = "Update Configurations"
    
    def __str__(self):
        return f"Update config for {self.school.name}"


class SecurityReview(models.Model):
    """
    Security review reminders and logs
    """
    REVIEW_TYPES = [
        ('password_policy', 'Password Policy Review'),
        ('access_audit', 'Access Rights Audit'),
        ('security_scan', 'Security Scan'),
        ('backup_test', 'Backup Recovery Test'),
        ('penetration_test', 'Penetration Test'),
    ]
    
    STATUSES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('skipped', 'Skipped'),
    ]
    
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='security_reviews')
    review_type = models.CharField(max_length=50, choices=REVIEW_TYPES)
    due_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    notes = models.TextField(blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    findings = models.JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = "Security Review"
        verbose_name_plural = "Security Reviews"
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.school.name} - {self.get_review_type_display()}"


class ActivityMonitoring(models.Model):
    """
    Real-time activity monitoring
    """
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=100, blank=True)
    resource_id = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['school', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{user_str} - {self.action} [{self.timestamp}]"
