from django.urls import path
from . import views

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
]