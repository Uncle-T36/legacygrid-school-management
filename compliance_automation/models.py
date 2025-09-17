from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class ComplianceFramework(models.Model):
    """Model for different compliance frameworks (GDPR, CCPA, POPIA, etc.)"""
    FRAMEWORK_TYPES = [
        ('gdpr', 'GDPR (EU General Data Protection Regulation)'),
        ('ccpa', 'CCPA (California Consumer Privacy Act)'),
        ('popia', 'POPIA (Protection of Personal Information Act - South Africa)'),
        ('coppa', 'COPPA (Children\'s Online Privacy Protection Act)'),
        ('ferpa', 'FERPA (Family Educational Rights and Privacy Act)'),
        ('pipeda', 'PIPEDA (Personal Information Protection and Electronic Documents Act - Canada)'),
        ('custom', 'Custom Framework'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Implementation'),
        ('inactive', 'Inactive'),
        ('under_review', 'Under Review'),
    ]
    
    name = models.CharField(max_length=255)
    framework_type = models.CharField(max_length=20, choices=FRAMEWORK_TYPES)
    description = models.TextField()
    applicable_regions = models.JSONField(default=list)  # List of countries/regions
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    implementation_date = models.DateField(null=True, blank=True)
    review_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Owner control
    is_owner_managed = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['framework_type', 'status']),
            models.Index(fields=['status', 'implementation_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_framework_type_display()})"


class ConsentManagement(models.Model):
    """Model for managing user consents"""
    CONSENT_TYPES = [
        ('data_processing', 'Data Processing'),
        ('marketing', 'Marketing Communications'),
        ('cookies', 'Cookie Usage'),
        ('third_party_sharing', 'Third-Party Data Sharing'),
        ('analytics', 'Analytics and Tracking'),
        ('educational_records', 'Educational Records Access'),
    ]
    
    STATUS_CHOICES = [
        ('granted', 'Granted'),
        ('denied', 'Denied'),
        ('withdrawn', 'Withdrawn'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(max_length=30, choices=CONSENT_TYPES)
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    granted_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    consent_text = models.TextField()  # The exact text the user consented to
    version = models.CharField(max_length=10, default='1.0')
    
    # Audit trail
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'consent_type', 'framework', 'version']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['framework', 'consent_type']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_consent_type_display()} ({self.status})"


class DataRetentionPolicy(models.Model):
    """Model for data retention policies"""
    DATA_TYPES = [
        ('user_profiles', 'User Profiles'),
        ('educational_records', 'Educational Records'),
        ('financial_records', 'Financial Records'),
        ('communication_logs', 'Communication Logs'),
        ('system_logs', 'System Logs'),
        ('backup_data', 'Backup Data'),
        ('analytics_data', 'Analytics Data'),
    ]
    
    RETENTION_UNITS = [
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years'),
    ]
    
    name = models.CharField(max_length=255)
    data_type = models.CharField(max_length=30, choices=DATA_TYPES)
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE)
    retention_period = models.PositiveIntegerField()
    retention_unit = models.CharField(max_length=10, choices=RETENTION_UNITS)
    description = models.TextField()
    automated_deletion = models.BooleanField(default=True)
    notification_before_deletion = models.PositiveIntegerField(default=30)  # days
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['data_type', 'retention_period']
        unique_together = ['data_type', 'framework']
    
    def __str__(self):
        return f"{self.get_data_type_display()} - {self.retention_period} {self.retention_unit}"


class ComplianceAudit(models.Model):
    """Model for compliance audit logs"""
    AUDIT_TYPES = [
        ('data_access', 'Data Access'),
        ('data_modification', 'Data Modification'),
        ('data_deletion', 'Data Deletion'),
        ('consent_change', 'Consent Change'),
        ('policy_update', 'Policy Update'),
        ('export_request', 'Data Export Request'),
        ('deletion_request', 'Data Deletion Request'),
    ]
    
    COMPLIANCE_STATUS = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('under_review', 'Under Review'),
        ('remediated', 'Remediated'),
    ]
    
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='audit_logs')
    affected_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='affected_audit_logs', null=True, blank=True)
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE)
    action_description = models.TextField()
    data_fields_accessed = models.JSONField(default=list)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    compliance_status = models.CharField(max_length=20, choices=COMPLIANCE_STATUS, default='compliant')
    metadata = models.JSONField(default=dict)
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['audit_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['framework', 'compliance_status']),
        ]
    
    def __str__(self):
        return f"{self.get_audit_type_display()} by {self.user.username} at {self.timestamp}"


class LegalDisclaimer(models.Model):
    """Model for country/region-specific legal disclaimers"""
    DISCLAIMER_TYPES = [
        ('privacy_policy', 'Privacy Policy'),
        ('terms_of_service', 'Terms of Service'),
        ('cookie_policy', 'Cookie Policy'),
        ('data_processing_notice', 'Data Processing Notice'),
        ('parental_consent', 'Parental Consent Notice'),
        ('educational_records', 'Educational Records Disclaimer'),
    ]
    
    title = models.CharField(max_length=255)
    disclaimer_type = models.CharField(max_length=30, choices=DISCLAIMER_TYPES)
    country_code = models.CharField(max_length=2)  # ISO 3166-1 alpha-2
    region = models.CharField(max_length=100, blank=True)
    language_code = models.CharField(max_length=5, default='en')  # ISO 639-1
    content = models.TextField()
    version = models.CharField(max_length=10, default='1.0')
    effective_date = models.DateField()
    is_active = models.BooleanField(default=True)
    requires_acceptance = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date']
        unique_together = ['disclaimer_type', 'country_code', 'language_code', 'version']
        indexes = [
            models.Index(fields=['country_code', 'is_active']),
            models.Index(fields=['disclaimer_type', 'effective_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.country_code}) v{self.version}"


class ComplianceReport(models.Model):
    """Model for compliance reports and assessments"""
    REPORT_TYPES = [
        ('monthly', 'Monthly Compliance Report'),
        ('quarterly', 'Quarterly Assessment'),
        ('annual', 'Annual Compliance Review'),
        ('incident', 'Incident Report'),
        ('audit', 'External Audit Report'),
        ('custom', 'Custom Report'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    summary = models.TextField()
    detailed_findings = models.TextField()
    recommendations = models.TextField()
    compliance_score = models.FloatField(null=True, blank=True)  # 0-100
    period_start = models.DateField()
    period_end = models.DateField()
    
    # File attachments
    report_file = models.FileField(upload_to='compliance_reports/', null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['framework', 'report_type']),
            models.Index(fields=['status', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.period_start} - {self.period_end})"