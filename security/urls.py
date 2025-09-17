"""
URL configuration for security app
"""
from django.urls import path, include
from . import views

app_name = 'security'

urlpatterns = [
    # Security dashboard
    path('dashboard/', views.security_dashboard, name='dashboard'),
    
    # Audit logs
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('security-events/', views.security_events, name='security_events'),
    
    # License management
    path('license/', views.license_management, name='license_management'),
    path('license/validate/', views.validate_license, name='validate_license'),
    
    # IP Whitelist management
    path('ip-whitelist/', views.ip_whitelist, name='ip_whitelist'),
    
    # 2FA management
    path('2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('2fa/backup-codes/', views.backup_codes, name='backup_codes'),
    
    # Clone detection
    path('fingerprint/', views.environment_fingerprint, name='fingerprint'),
    path('clone-detection/', views.clone_detection, name='clone_detection'),
]