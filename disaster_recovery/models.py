from django.db import models
from django.conf import settings
from django.utils import timezone


class BackupSnapshot(models.Model):
    """Model to track backup snapshots with versioning"""
    BACKUP_TYPES = [
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup'),
        ('differential', 'Differential Backup'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=255)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # Size in bytes
    checksum = models.CharField(max_length=64, blank=True)  # SHA-256 checksum
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Owner control - only owner can manage backups
    is_owner_managed = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['backup_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.backup_type}) - {self.status}"


class FailoverConfiguration(models.Model):
    """Model to manage failover configurations"""
    name = models.CharField(max_length=255)
    primary_server = models.CharField(max_length=255)
    backup_server = models.CharField(max_length=255)
    health_check_url = models.URLField()
    health_check_interval = models.PositiveIntegerField(default=30)  # seconds
    failover_threshold = models.PositiveIntegerField(default=3)  # failed checks before failover
    is_active = models.BooleanField(default=False)
    last_health_check = models.DateTimeField(null=True, blank=True)
    current_status = models.CharField(max_length=50, default='healthy')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['name', 'created_by']
    
    def __str__(self):
        return f"{self.name} - {self.current_status}"


class DowntimeNotification(models.Model):
    """Model to track downtime notifications"""
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
        ('in_app', 'In-App'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    recipients = models.JSONField(default=list)  # List of email/phone numbers
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.notification_type}"