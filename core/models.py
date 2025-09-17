from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Country(models.Model):
    """Model for supported countries with localization settings"""
    
    code = models.CharField(max_length=3, unique=True, help_text="ISO 3166-1 alpha-3 country code")
    name = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=3, default='USD', help_text="ISO 4217 currency code")
    timezone = models.CharField(max_length=50, default='UTC')
    locale = models.CharField(max_length=10, default='en-US', help_text="Language and region code")
    is_rtl = models.BooleanField(default=False, help_text="Right-to-left language support")
    date_format = models.CharField(max_length=20, default='%Y-%m-%d')
    time_format = models.CharField(max_length=20, default='%H:%M')
    is_active = models.BooleanField(default=True)
    
    # Payment gateway settings per country
    supported_payment_gateways = models.JSONField(default=list, help_text="List of enabled payment gateways")
    
    # Regulatory settings
    data_retention_days = models.IntegerField(default=2555, help_text="Data retention period in days (7 years default)")
    gdpr_compliant = models.BooleanField(default=False)
    requires_consent = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Tenant(models.Model):
    """Multi-tenant support for school organizations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    subdomain = models.SlugField(max_length=50, unique=True, help_text="Unique subdomain identifier")
    domain = models.CharField(max_length=200, blank=True, help_text="Custom domain if applicable")
    
    # Location and localization
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    
    # Branding
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#007bff', help_text="Primary brand color (hex)")
    secondary_color = models.CharField(max_length=7, default='#6c757d', help_text="Secondary brand color (hex)")
    custom_css = models.TextField(blank=True, help_text="Custom CSS for tenant-specific styling")
    
    # Contact information
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Subscription and billing
    subscription_tier = models.CharField(max_length=50, default='free')
    is_active = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Feature toggles (owner-configurable)
    enabled_features = models.JSONField(default=list, help_text="List of enabled features for this tenant")
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_tenants')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def is_trial_active(self):
        """Check if trial period is still active"""
        return self.trial_ends_at and self.trial_ends_at > timezone.now()


class PaymentGateway(models.Model):
    """Configuration for different payment gateways"""
    
    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('paypal', 'PayPal'),
        ('mpesa', 'M-Pesa'),
        ('ecocash', 'EcoCash'),
        ('onemoney', 'OneMoney'),
        ('razorpay', 'Razorpay'),
    ]
    
    name = models.CharField(max_length=50, choices=GATEWAY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    
    # Configuration (encrypted in production)
    config = models.JSONField(default=dict, help_text="Gateway-specific configuration")
    
    # Supported features
    supports_recurring = models.BooleanField(default=False)
    supports_webhooks = models.BooleanField(default=False)
    supported_currencies = models.JSONField(default=list)
    
    # Restrictions (owner-only configurable)
    allowed_countries = models.ManyToManyField(Country, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name


class FeatureToggle(models.Model):
    """Feature toggle system for granular control"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_global = models.BooleanField(default=False, help_text="If true, applies globally; if false, can be set per tenant")
    is_enabled_globally = models.BooleanField(default=False)
    
    # Owner-only control
    requires_owner_approval = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class TenantFeatureToggle(models.Model):
    """Per-tenant feature toggle settings"""
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    feature = models.ForeignKey(FeatureToggle, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=False)
    
    # Approval tracking
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tenant', 'feature']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.feature.name}: {'Enabled' if self.is_enabled else 'Disabled'}"


class AuditLog(models.Model):
    """Comprehensive audit logging for compliance"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('payment', 'Payment'),
        ('export', 'Data Export'),
        ('config_change', 'Configuration Change'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource = models.CharField(max_length=100, help_text="Model name or resource identifier")
    resource_id = models.CharField(max_length=100, blank=True)
    
    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Change details
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    # Additional context
    notes = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['tenant', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.resource} by {self.user} at {self.timestamp}"