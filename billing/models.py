from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
import uuid


class Currency(models.Model):
    """Supported currencies for multi-currency billing"""
    code = models.CharField(max_length=3, unique=True, help_text="ISO 4217 currency code")
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    exchange_rate_to_usd = models.DecimalField(max_digits=10, decimal_places=6, default=1.0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class SubscriptionTier(models.Model):
    """Available subscription tiers"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    features = models.JSONField(default=list)  # List of feature names
    ai_access = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class SubscriptionPrice(models.Model):
    """Pricing for subscription tiers in different currencies"""
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE, related_name='prices')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['tier', 'currency']
    
    def __str__(self):
        return f"{self.tier.name} - {self.currency.code} {self.monthly_price}/month"


class UserSubscription(models.Model):
    """User subscription status"""
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    external_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    payment_provider = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.tier.name} ({self.status})"
    
    @property
    def is_active(self):
        return (self.status == 'active' and 
                (self.expires_at is None or self.expires_at > timezone.now()))
    
    def has_feature(self, feature_name):
        """Check if user has access to a specific feature"""
        if not self.is_active:
            return feature_name in settings.SUBSCRIPTION_TIERS.get('free', {}).get('features', [])
        return feature_name in self.tier.features


class PaymentProvider(models.Model):
    """Supported payment providers"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    supports_webhooks = models.BooleanField(default=False)
    supported_currencies = models.ManyToManyField(Currency, blank=True)
    configuration = models.JSONField(default=dict)  # Provider-specific config
    
    def __str__(self):
        return self.display_name


class Payment(models.Model):
    """Payment records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    external_payment_id = models.CharField(max_length=255, blank=True)
    external_customer_id = models.CharField(max_length=255, blank=True)
    
    metadata = models.JSONField(default=dict)  # Additional payment data
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {str(self.id)[:8]} - {self.amount} {self.currency.code} ({self.status})"


class WebhookEvent(models.Model):
    """Log webhook events from payment providers"""
    EVENT_TYPES = [
        ('payment.succeeded', 'Payment Succeeded'),
        ('payment.failed', 'Payment Failed'),
        ('subscription.created', 'Subscription Created'),
        ('subscription.updated', 'Subscription Updated'),
        ('subscription.cancelled', 'Subscription Cancelled'),
        ('invoice.payment_succeeded', 'Invoice Payment Succeeded'),
        ('invoice.payment_failed', 'Invoice Payment Failed'),
    ]
    
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    external_event_id = models.CharField(max_length=255, unique=True)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider.name} - {self.event_type} ({self.external_event_id})"


class BillingAuditLog(models.Model):
    """Audit log for billing operations"""
    ACTION_TYPES = [
        ('subscription_created', 'Subscription Created'),
        ('subscription_updated', 'Subscription Updated'),
        ('subscription_cancelled', 'Subscription Cancelled'),
        ('payment_created', 'Payment Created'),
        ('payment_updated', 'Payment Updated'),
        ('tier_changed', 'Tier Changed'),
        ('webhook_processed', 'Webhook Processed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    admin_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, 
        related_name='billing_admin_actions'
    )
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} - {self.user or 'System'} at {self.created_at}"
