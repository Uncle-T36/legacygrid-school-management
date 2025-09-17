from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from functools import wraps
from .models import (
    ComplianceFramework, ConsentManagement, DataRetentionPolicy, 
    ComplianceAudit, LegalDisclaimer, ComplianceReport
)
import json
from datetime import datetime, timedelta


def owner_only(view_func):
    """
    Decorator that restricts access to only the owner (Uncle-T36).
    Redirects unauthorized users to the 'not_authorized' page.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.username == settings.BILLING_OWNER_USERNAME:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('not_authorized')
    return _wrapped_view


@owner_only
def compliance_dashboard(request):
    """
    Compliance automation dashboard - only accessible to Uncle-T36
    """
    # Get compliance statistics
    frameworks = ComplianceFramework.objects.filter(created_by=request.user)
    active_frameworks = frameworks.filter(status='active')
    
    # Recent consent changes
    recent_consents = ConsentManagement.objects.select_related('user', 'framework').order_by('-updated_at')[:10]
    
    # Upcoming policy reviews
    thirty_days_ahead = timezone.now().date() + timedelta(days=30)
    upcoming_reviews = frameworks.filter(review_date__lte=thirty_days_ahead, status='active')
    
    # Recent audit activities
    recent_audits = ComplianceAudit.objects.select_related('user', 'framework').order_by('-timestamp')[:10]
    
    # Compliance score calculation
    total_audits = ComplianceAudit.objects.filter(framework__in=active_frameworks).count()
    compliant_audits = ComplianceAudit.objects.filter(
        framework__in=active_frameworks, 
        compliance_status='compliant'
    ).count()
    compliance_score = (compliant_audits / total_audits * 100) if total_audits > 0 else 100
    
    context = {
        'frameworks_count': frameworks.count(),
        'active_frameworks_count': active_frameworks.count(),
        'recent_consents': recent_consents,
        'upcoming_reviews': upcoming_reviews,
        'recent_audits': recent_audits,
        'compliance_score': round(compliance_score, 1),
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'compliance_automation/dashboard.html', context)


@owner_only
def framework_management(request):
    """
    Compliance framework management - owner only
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        framework_type = request.POST.get('framework_type')
        description = request.POST.get('description')
        applicable_regions = request.POST.getlist('applicable_regions')
        implementation_date = request.POST.get('implementation_date')
        review_date = request.POST.get('review_date')
        
        framework = ComplianceFramework.objects.create(
            name=name,
            framework_type=framework_type,
            description=description,
            applicable_regions=applicable_regions,
            implementation_date=implementation_date if implementation_date else None,
            review_date=review_date if review_date else None,
            created_by=request.user
        )
        
        messages.success(request, f'Compliance framework "{name}" created successfully!')
        return redirect('framework_management')
    
    frameworks = ComplianceFramework.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'frameworks': frameworks,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'compliance_automation/framework_management.html', context)


@owner_only
def consent_management(request):
    """
    Consent management interface - owner only
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'bulk_update':
            # Handle bulk consent updates
            consent_ids = request.POST.getlist('consent_ids')
            new_status = request.POST.get('new_status')
            
            updated_count = ConsentManagement.objects.filter(
                id__in=consent_ids
            ).update(
                status=new_status,
                updated_at=timezone.now()
            )
            
            messages.success(request, f'Updated {updated_count} consent records.')
            return redirect('consent_management')
    
    # Filter consents
    framework_filter = request.GET.get('framework')
    status_filter = request.GET.get('status')
    consent_type_filter = request.GET.get('consent_type')
    
    consents = ConsentManagement.objects.select_related('user', 'framework').order_by('-updated_at')
    
    if framework_filter:
        consents = consents.filter(framework_id=framework_filter)
    if status_filter:
        consents = consents.filter(status=status_filter)
    if consent_type_filter:
        consents = consents.filter(consent_type=consent_type_filter)
    
    # Pagination
    consents = consents[:100]  # Limit for performance
    
    frameworks = ComplianceFramework.objects.filter(created_by=request.user, status='active')
    
    context = {
        'consents': consents,
        'frameworks': frameworks,
        'selected_framework': framework_filter,
        'selected_status': status_filter,
        'selected_consent_type': consent_type_filter,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'compliance_automation/consent_management.html', context)


@owner_only
def data_retention_policies(request):
    """
    Data retention policy management - owner only
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        data_type = request.POST.get('data_type')
        framework_id = request.POST.get('framework')
        retention_period = request.POST.get('retention_period')
        retention_unit = request.POST.get('retention_unit')
        description = request.POST.get('description')
        automated_deletion = request.POST.get('automated_deletion') == 'on'
        notification_before_deletion = request.POST.get('notification_before_deletion', 30)
        
        framework = get_object_or_404(ComplianceFramework, id=framework_id, created_by=request.user)
        
        policy = DataRetentionPolicy.objects.create(
            name=name,
            data_type=data_type,
            framework=framework,
            retention_period=int(retention_period),
            retention_unit=retention_unit,
            description=description,
            automated_deletion=automated_deletion,
            notification_before_deletion=int(notification_before_deletion),
            created_by=request.user
        )
        
        messages.success(request, f'Data retention policy "{name}" created successfully!')
        return redirect('data_retention_policies')
    
    policies = DataRetentionPolicy.objects.select_related('framework').filter(
        created_by=request.user
    ).order_by('-created_at')
    
    frameworks = ComplianceFramework.objects.filter(created_by=request.user, status='active')
    
    context = {
        'policies': policies,
        'frameworks': frameworks,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'compliance_automation/data_retention_policies.html', context)


@owner_only
def legal_disclaimers(request):
    """
    Legal disclaimer management - owner only
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        disclaimer_type = request.POST.get('disclaimer_type')
        country_code = request.POST.get('country_code')
        region = request.POST.get('region', '')
        language_code = request.POST.get('language_code', 'en')
        content = request.POST.get('content')
        version = request.POST.get('version', '1.0')
        effective_date = request.POST.get('effective_date')
        requires_acceptance = request.POST.get('requires_acceptance') == 'on'
        
        disclaimer = LegalDisclaimer.objects.create(
            title=title,
            disclaimer_type=disclaimer_type,
            country_code=country_code.upper(),
            region=region,
            language_code=language_code,
            content=content,
            version=version,
            effective_date=effective_date,
            requires_acceptance=requires_acceptance,
            created_by=request.user
        )
        
        messages.success(request, f'Legal disclaimer "{title}" created successfully!')
        return redirect('legal_disclaimers')
    
    disclaimers = LegalDisclaimer.objects.filter(created_by=request.user).order_by('-effective_date')
    
    context = {
        'disclaimers': disclaimers,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'compliance_automation/legal_disclaimers.html', context)


@owner_only
def compliance_reports(request):
    """
    Compliance reporting interface - owner only
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        report_type = request.POST.get('report_type')
        framework_id = request.POST.get('framework')
        summary = request.POST.get('summary')
        detailed_findings = request.POST.get('detailed_findings')
        recommendations = request.POST.get('recommendations')
        period_start = request.POST.get('period_start')
        period_end = request.POST.get('period_end')
        
        framework = get_object_or_404(ComplianceFramework, id=framework_id, created_by=request.user)
        
        # Calculate compliance score for the period
        audits_in_period = ComplianceAudit.objects.filter(
            framework=framework,
            timestamp__date__range=[period_start, period_end]
        )
        total_audits = audits_in_period.count()
        compliant_audits = audits_in_period.filter(compliance_status='compliant').count()
        compliance_score = (compliant_audits / total_audits * 100) if total_audits > 0 else 100
        
        report = ComplianceReport.objects.create(
            title=title,
            report_type=report_type,
            framework=framework,
            summary=summary,
            detailed_findings=detailed_findings,
            recommendations=recommendations,
            compliance_score=round(compliance_score, 1),
            period_start=period_start,
            period_end=period_end,
            created_by=request.user
        )
        
        messages.success(request, f'Compliance report "{title}" created successfully!')
        return redirect('compliance_reports')
    
    reports = ComplianceReport.objects.select_related('framework').filter(
        created_by=request.user
    ).order_by('-period_end')
    
    frameworks = ComplianceFramework.objects.filter(created_by=request.user, status='active')
    
    context = {
        'reports': reports,
        'frameworks': frameworks,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'compliance_automation/compliance_reports.html', context)


@owner_only
def audit_logs(request):
    """
    Compliance audit logs viewer - owner only
    """
    # Filter parameters
    framework_filter = request.GET.get('framework')
    audit_type_filter = request.GET.get('audit_type')
    compliance_status_filter = request.GET.get('compliance_status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    audits = ComplianceAudit.objects.select_related('user', 'framework').order_by('-timestamp')
    
    # Apply filters
    if framework_filter:
        audits = audits.filter(framework_id=framework_filter)
    if audit_type_filter:
        audits = audits.filter(audit_type=audit_type_filter)
    if compliance_status_filter:
        audits = audits.filter(compliance_status=compliance_status_filter)
    if date_from:
        audits = audits.filter(timestamp__date__gte=date_from)
    if date_to:
        audits = audits.filter(timestamp__date__lte=date_to)
    
    # Pagination
    audits = audits[:500]  # Limit for performance
    
    frameworks = ComplianceFramework.objects.filter(created_by=request.user)
    
    context = {
        'audits': audits,
        'frameworks': frameworks,
        'selected_framework': framework_filter,
        'selected_audit_type': audit_type_filter,
        'selected_compliance_status': compliance_status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'compliance_automation/audit_logs.html', context)


@owner_only
def compliance_api_stats(request):
    """
    API endpoint for compliance statistics
    """
    if request.method == 'GET':
        frameworks = ComplianceFramework.objects.filter(created_by=request.user)
        
        # Framework statistics
        framework_stats = frameworks.values('status').annotate(count=Count('id'))
        
        # Consent statistics
        consent_stats = ConsentManagement.objects.filter(
            framework__in=frameworks
        ).values('status').annotate(count=Count('id'))
        
        # Recent audit activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_audits = ComplianceAudit.objects.filter(
            framework__in=frameworks,
            timestamp__gte=thirty_days_ago
        ).values('compliance_status').annotate(count=Count('id'))
        
        # Policy compliance summary
        total_policies = DataRetentionPolicy.objects.filter(
            framework__in=frameworks,
            is_active=True
        ).count()
        
        return JsonResponse({
            'framework_stats': list(framework_stats),
            'consent_stats': list(consent_stats),
            'recent_audit_stats': list(recent_audits),
            'total_active_policies': total_policies,
            'total_frameworks': frameworks.count(),
            'active_frameworks': frameworks.filter(status='active').count(),
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)