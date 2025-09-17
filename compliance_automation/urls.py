from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.compliance_dashboard, name='compliance_dashboard'),
    path('frameworks/', views.framework_management, name='framework_management'),
    path('consents/', views.consent_management, name='consent_management'),
    path('data-retention/', views.data_retention_policies, name='data_retention_policies'),
    path('disclaimers/', views.legal_disclaimers, name='legal_disclaimers'),
    path('reports/', views.compliance_reports, name='compliance_reports'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('api/stats/', views.compliance_api_stats, name='compliance_api_stats'),
]