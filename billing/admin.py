from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    Currency, SubscriptionTier, SubscriptionPrice, UserSubscription,
    PaymentProvider, Payment, WebhookEvent, BillingAuditLog
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'exchange_rate_to_usd', 'is_active', 'last_updated']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    readonly_fields = ['last_updated']


class SubscriptionPriceInline(admin.TabularInline):
    model = SubscriptionPrice
    extra = 0


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'ai_access', 'is_active', 'sort_order']
    list_filter = ['ai_access', 'is_active']
    search_fields = ['name', 'description']
    inlines = [SubscriptionPriceInline]


@admin.register(SubscriptionPrice)
class SubscriptionPriceAdmin(admin.ModelAdmin):
    list_display = ['tier', 'currency', 'monthly_price', 'annual_price', 'is_active']
    list_filter = ['tier', 'currency', 'is_active']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'tier', 'status', 'billing_cycle', 'started_at', 'expires_at']
    list_filter = ['status', 'tier', 'billing_cycle', 'currency']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['started_at']
    
    def has_change_permission(self, request, obj=None):
        # Only allow Uncle-T36 to modify subscriptions
        if not request.user.username == 'Uncle-T36' and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_active', 'supports_webhooks']
    list_filter = ['is_active', 'supports_webhooks']
    filter_horizontal = ['supported_currencies']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'currency', 'status', 'provider', 'created_at']
    list_filter = ['status', 'provider', 'currency', 'created_at']
    search_fields = ['user__username', 'user__email', 'external_payment_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def has_change_permission(self, request, obj=None):
        # Only allow Uncle-T36 to modify payments
        if not request.user.username == 'Uncle-T36' and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['provider', 'event_type', 'external_event_id', 'processed', 'created_at']
    list_filter = ['provider', 'event_type', 'processed', 'created_at']
    search_fields = ['external_event_id']
    readonly_fields = ['created_at', 'processed_at']


@admin.register(BillingAuditLog)
class BillingAuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'admin_user', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'admin_user__username', 'description']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False  # Audit logs should only be created programmatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Audit logs should be immutable
