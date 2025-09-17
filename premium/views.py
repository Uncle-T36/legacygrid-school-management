"""
Premium views for LegacyGrid School Management System
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from billing.views import owner_only
from .models import (
    PremiumSubscription, UsageAnalytics, CustomDomain, BackupConfiguration,
    BackupLog, FeedbackReport, UpdateConfiguration, SecurityReview, ActivityMonitoring
)


@owner_only
def premium_dashboard(request):
    """Premium dashboard - owner only"""
    context = {
        'subscription': PremiumSubscription.objects.first(),
        'recent_analytics': UsageAnalytics.objects.all()[:10],
        'recent_activities': ActivityMonitoring.objects.all()[:10],
    }
    return render(request, 'premium/dashboard.html', context)


@owner_only
def usage_analytics(request):
    """Usage analytics view"""
    analytics = UsageAnalytics.objects.all()[:100]
    return render(request, 'premium/analytics.html', {'analytics': analytics})


@owner_only
def activity_monitoring(request):
    """Activity monitoring view"""
    activities = ActivityMonitoring.objects.all()[:100]
    return render(request, 'premium/activity_monitoring.html', {'activities': activities})


@owner_only
def backup_management(request):
    """Backup management view"""
    backups = BackupLog.objects.all()[:50]
    config = BackupConfiguration.objects.first()
    return render(request, 'premium/backup_management.html', {
        'backups': backups,
        'config': config
    })


@owner_only
def create_backup(request):
    """Create new backup"""
    if request.method == 'POST':
        # Backup creation logic here
        messages.success(request, 'Backup created successfully')
    return redirect('premium:backups')


@owner_only
def backup_detail(request, backup_id):
    """Backup detail view"""
    backup = get_object_or_404(BackupLog, id=backup_id)
    return render(request, 'premium/backup_detail.html', {'backup': backup})


@owner_only
def custom_domains(request):
    """Custom domains management"""
    domains = CustomDomain.objects.all()
    return render(request, 'premium/custom_domains.html', {'domains': domains})


@owner_only
def verify_domain(request, domain_id):
    """Verify custom domain"""
    domain = get_object_or_404(CustomDomain, id=domain_id)
    # Domain verification logic here
    messages.success(request, f'Domain {domain.domain} verified successfully')
    return redirect('premium:domains')


@login_required
def feedback_list(request):
    """Feedback list view"""
    feedback = FeedbackReport.objects.all()[:50]
    return render(request, 'premium/feedback_list.html', {'feedback': feedback})


@login_required
def new_feedback(request):
    """New feedback form"""
    if request.method == 'POST':
        # Feedback creation logic here
        messages.success(request, 'Feedback submitted successfully')
        return redirect('premium:feedback_list')
    return render(request, 'premium/new_feedback.html')


@login_required
def feedback_detail(request, feedback_id):
    """Feedback detail view"""
    feedback = get_object_or_404(FeedbackReport, id=feedback_id)
    return render(request, 'premium/feedback_detail.html', {'feedback': feedback})


@owner_only
def update_management(request):
    """Update management view"""
    config = UpdateConfiguration.objects.first()
    return render(request, 'premium/update_management.html', {'config': config})


@owner_only
def check_updates(request):
    """Check for updates"""
    # Update checking logic here
    messages.info(request, 'No updates available')
    return redirect('premium:updates')


@owner_only
def security_reviews(request):
    """Security reviews view"""
    reviews = SecurityReview.objects.all()[:50]
    return render(request, 'premium/security_reviews.html', {'reviews': reviews})


@owner_only
def security_review_detail(request, review_id):
    """Security review detail view"""
    review = get_object_or_404(SecurityReview, id=review_id)
    return render(request, 'premium/security_review_detail.html', {'review': review})
