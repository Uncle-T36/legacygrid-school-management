from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Currency, SubscriptionPlan, PaymentProvider, UserProfile,
    Subscription, Payment, WebhookEvent, MessageTemplate, NotificationLog
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'exchange_rate_to_usd', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_usd', 'duration_days', 'max_students', 'max_teachers', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']
    ordering = ['price_usd']


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider_type', 'is_active', 'is_zimbabwe_default', 'created_at']
    list_filter = ['provider_type', 'is_active', 'is_zimbabwe_default']
    search_fields = ['name']
    filter_horizontal = ['supported_currencies']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_language', 'preferred_currency', 'phone_number', 'country']
    list_filter = ['preferred_language', 'country', 'preferred_currency']
    search_fields = ['user__username', 'user__email', 'phone_number']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew', 'is_active_display']
    list_filter = ['status', 'plan', 'auto_renew']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'created_at'
    
    def is_active_display(self, obj):
        if obj.is_active():
            return format_html('<span style="color: green;">✓ Active</span>')
        else:
            return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_display.short_description = 'Currently Active'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount_display', 'provider', 'status', 'created_at']
    list_filter = ['status', 'provider', 'currency']
    search_fields = ['user__username', 'provider_transaction_id', 'provider_reference']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'amount_usd', 'exchange_rate']
    
    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency.code} (${obj.amount_usd})"
    amount_display.short_description = 'Amount'


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['provider', 'event_type', 'event_id', 'processed', 'created_at']
    list_filter = ['provider', 'processed', 'event_type']
    search_fields = ['event_id', 'event_type']
    date_hierarchy = 'created_at'
    readonly_fields = ['payload']


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'message_type', 'channel', 'language', 'is_active']
    list_filter = ['message_type', 'channel', 'language', 'is_active']
    search_fields = ['name', 'content']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'template', 'channel', 'recipient', 'status', 'created_at']
    list_filter = ['channel', 'status', 'template__message_type']
    search_fields = ['user__username', 'recipient']
    date_hierarchy = 'created_at'
