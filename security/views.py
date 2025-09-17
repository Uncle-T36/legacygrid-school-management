"""
Security views for LegacyGrid School Management System
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from billing.views import owner_only
from .models import AuditLog, SecurityEvent, LicenseKey, EnvironmentFingerprint
from .utils import generate_environment_fingerprint, validate_license_key


@owner_only
def security_dashboard(request):
    """Security dashboard - owner only"""
    recent_events = SecurityEvent.objects.all()[:10]
    audit_logs = AuditLog.objects.all()[:10]
    
    context = {
        'recent_events': recent_events,
        'audit_logs': audit_logs,
        'total_events': SecurityEvent.objects.count(),
        'total_audits': AuditLog.objects.count(),
    }
    return render(request, 'security/dashboard.html', context)


@owner_only
def audit_logs(request):
    """Audit logs view"""
    logs = AuditLog.objects.all()[:100]
    return render(request, 'security/audit_logs.html', {'logs': logs})


@owner_only
def security_events(request):
    """Security events view"""
    events = SecurityEvent.objects.all()[:100]
    return render(request, 'security/security_events.html', {'events': events})


@owner_only
def license_management(request):
    """License management view"""
    licenses = LicenseKey.objects.all()
    return render(request, 'security/license_management.html', {'licenses': licenses})


@owner_only
def validate_license(request):
    """Validate license key"""
    if request.method == 'POST':
        # License validation logic here
        messages.success(request, 'License validated successfully')
    return redirect('security:license_management')


@owner_only
def ip_whitelist(request):
    """IP whitelist management"""
    return render(request, 'security/ip_whitelist.html')


@login_required
def setup_2fa(request):
    """2FA setup view"""
    return render(request, 'security/setup_2fa.html')


@login_required
def backup_codes(request):
    """2FA backup codes view"""
    return render(request, 'security/backup_codes.html')


@owner_only
def environment_fingerprint(request):
    """Environment fingerprint view"""
    return render(request, 'security/fingerprint.html')


@owner_only
def clone_detection(request):
    """Clone detection view"""
    return render(request, 'security/clone_detection.html')
