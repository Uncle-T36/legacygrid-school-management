from django.contrib import admin
from .models import Country, Tenant, PaymentGateway, FeatureToggle, TenantFeatureToggle, AuditLog

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'currency_code', 'locale', 'is_rtl', 'is_active']
    list_filter = ['is_active', 'is_rtl', 'gdpr_compliant']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'country', 'subscription_tier', 'is_active', 'created_at']
    list_filter = ['subscription_tier', 'is_active', 'country']
    search_fields = ['name', 'subdomain', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'is_active', 'supports_recurring', 'supports_webhooks']
    list_filter = ['is_active', 'supports_recurring', 'supports_webhooks']
    search_fields = ['name', 'display_name']


@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_global', 'is_enabled_globally', 'requires_owner_approval']
    list_filter = ['is_global', 'is_enabled_globally', 'requires_owner_approval']
    search_fields = ['name', 'description']


@admin.register(TenantFeatureToggle)
class TenantFeatureToggleAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'feature', 'is_enabled', 'approved_by', 'approved_at']
    list_filter = ['is_enabled', 'feature']
    search_fields = ['tenant__name', 'feature__name']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'action', 'resource', 'timestamp']
    list_filter = ['action', 'timestamp', 'tenant']
    search_fields = ['user__username', 'resource', 'notes']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        # Audit logs should not be manually created
        return False
    
    def has_change_permission(self, request, obj=None):
        # Audit logs should not be edited
        return False