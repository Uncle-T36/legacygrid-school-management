from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class Currency(models.Model):
    """Supported currencies for payments"""
    code = models.CharField(max_length=3, unique=True)  # USD, ZWL, ZAR, NGN, etc.
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    exchange_rate_to_usd = models.DecimalField(max_digits=15, decimal_places=6, default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name_plural = "Currencies"


class SubscriptionPlan(models.Model):
    """Different subscription plans for schools"""
    PLAN_TYPES = [
        ('basic', 'Basic Plan'),
        ('standard', 'Standard Plan'),
        ('premium', 'Premium Plan'),
        ('enterprise', 'Enterprise Plan'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)  # 30 days, 365 days, etc.
    max_students = models.IntegerField()
    max_teachers = models.IntegerField()
    features = models.JSONField(default=list)  # List of features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ${self.price_usd}"


class PaymentProvider(models.Model):
    """Payment providers (Stripe, PayPal, Mobile Money, etc.)"""
    PROVIDER_TYPES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('ecocash', 'EcoCash'),
        ('onemoney', 'OneMoney'),
        ('telecash', 'Telecash'),
        ('mtn_mobile_money', 'MTN Mobile Money'),
        ('airtel_money', 'Airtel Money'),
        ('mpesa', 'M-Pesa'),
        ('skrill', 'Skrill'),
        ('neteller', 'Neteller'),
    ]
    
    name = models.CharField(max_length=50)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPES)
    is_active = models.BooleanField(default=True)
    supported_currencies = models.ManyToManyField(Currency)
    config = models.JSONField(default=dict)  # Store API keys, etc.
    webhook_url = models.URLField(blank=True)
    is_zimbabwe_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile for language preferences and Zimbabwe localization"""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('sn', 'Shona'),
        ('nd', 'Ndebele'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    preferred_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='Zimbabwe')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Subscription(models.Model):
    """User subscriptions"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending Payment'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"


class Payment(models.Model):
    """Payment records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    
    # Amount in original currency
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    
    # Amount in USD for internal accounting
    amount_usd = models.DecimalField(max_digits=15, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Provider-specific transaction IDs
    provider_transaction_id = models.CharField(max_length=255, blank=True)
    provider_reference = models.CharField(max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.amount} {self.currency.code}"

    class Meta:
        ordering = ['-created_at']


class WebhookEvent(models.Model):
    """Store webhook events for processing"""
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    event_id = models.CharField(max_length=255)  # Provider's event ID
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.provider.name} - {self.event_type} - {self.event_id}"

    class Meta:
        unique_together = ['provider', 'event_id']


class MessageTemplate(models.Model):
    """Message templates for multi-language notifications"""
    MESSAGE_TYPES = [
        ('payment_success', 'Payment Success'),
        ('payment_failed', 'Payment Failed'),
        ('subscription_activated', 'Subscription Activated'),
        ('subscription_expired', 'Subscription Expired'),
        ('subscription_reminder', 'Subscription Reminder'),
    ]
    
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App Notification'),
    ]
    
    name = models.CharField(max_length=100)
    message_type = models.CharField(max_length=30, choices=MESSAGE_TYPES)
    channel = models.CharField(max_length=10, choices=CHANNEL_TYPES)
    language = models.CharField(max_length=2, choices=UserProfile.LANGUAGE_CHOICES)
    subject = models.CharField(max_length=200, blank=True)  # For email
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.language} - {self.channel}"

    class Meta:
        unique_together = ['message_type', 'channel', 'language']


class NotificationLog(models.Model):
    """Log of sent notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE)
    channel = models.CharField(max_length=10)
    recipient = models.CharField(max_length=255)  # email or phone number
    content = models.TextField()
    status = models.CharField(max_length=20, default='sent')
    provider_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.template.name} - {self.channel}"
