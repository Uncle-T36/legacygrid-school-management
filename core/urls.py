from django.urls import path
from . import views
from . import api_views

app_name = 'core'

urlpatterns = [
    # Owner-only international management
    path('international/', views.international_dashboard, name='international_dashboard'),
    path('countries/', views.manage_countries, name='manage_countries'),
    path('tenants/', views.manage_tenants, name='manage_tenants'),
    path('payment-gateways/', views.manage_payment_gateways, name='manage_payment_gateways'),
    path('features/', views.manage_features, name='manage_features'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('export/', views.export_data, name='export_data'),
    path('currency-converter/', views.currency_converter, name='currency_converter'),
    
    # Additional management features
    path('notifications/', api_views.notification_templates, name='notification_templates'),
    path('ministry-integration/', api_views.ministry_integration, name='ministry_integration'),
    path('cloud-settings/', api_views.cloud_settings, name='cloud_settings'),
    path('integrations/', api_views.integration_management, name='integration_management'),
    
    # API endpoints for mobile app
    path('api/school-info/', api_views.api_school_info, name='api_school_info'),
    path('api/currency-rates/', api_views.api_currency_rates, name='api_currency_rates'),
    path('api/features/', api_views.api_features, name='api_features'),
]