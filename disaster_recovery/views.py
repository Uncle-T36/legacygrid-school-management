from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from functools import wraps
from .models import BackupSnapshot, FailoverConfiguration, DowntimeNotification
import json
import subprocess
import os
import hashlib


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
def disaster_recovery_dashboard(request):
    """
    Disaster Recovery dashboard - only accessible to Uncle-T36
    """
    recent_backups = BackupSnapshot.objects.filter(created_by=request.user)[:10]
    active_failovers = FailoverConfiguration.objects.filter(
        created_by=request.user, 
        is_active=True
    )
    pending_notifications = DowntimeNotification.objects.filter(
        created_by=request.user,
        is_sent=False,
        scheduled_at__lte=timezone.now()
    )
    
    context = {
        'recent_backups': recent_backups,
        'active_failovers': active_failovers,
        'pending_notifications': pending_notifications,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'disaster_recovery/dashboard.html', context)


@owner_only
def backup_management(request):
    """
    Backup management interface - owner only
    """
    if request.method == 'POST':
        backup_type = request.POST.get('backup_type', 'full')
        backup_name = request.POST.get('backup_name', f'Backup-{timezone.now().strftime("%Y%m%d-%H%M%S")}')
        
        # Create backup snapshot record
        backup = BackupSnapshot.objects.create(
            name=backup_name,
            backup_type=backup_type,
            status='pending',
            created_by=request.user
        )
        
        # In demo mode, simulate backup completion
        if settings.DEMO_MODE:
            backup.status = 'completed'
            backup.completed_at = timezone.now()
            backup.file_size = 1024 * 1024 * 50  # 50MB simulated
            backup.checksum = 'demo_checksum_' + str(backup.id)
            backup.save()
            messages.success(request, f'Demo backup "{backup_name}" created successfully!')
        else:
            # In production, trigger actual backup process
            messages.info(request, f'Backup "{backup_name}" initiated. Check status in a few minutes.')
        
        return redirect('backup_management')
    
    backups = BackupSnapshot.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'backups': backups,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'disaster_recovery/backup_management.html', context)


@owner_only
def failover_configuration(request):
    """
    Failover configuration interface - owner only
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        primary_server = request.POST.get('primary_server')
        backup_server = request.POST.get('backup_server')
        health_check_url = request.POST.get('health_check_url')
        health_check_interval = int(request.POST.get('health_check_interval', 30))
        failover_threshold = int(request.POST.get('failover_threshold', 3))
        
        failover_config = FailoverConfiguration.objects.create(
            name=name,
            primary_server=primary_server,
            backup_server=backup_server,
            health_check_url=health_check_url,
            health_check_interval=health_check_interval,
            failover_threshold=failover_threshold,
            created_by=request.user
        )
        
        messages.success(request, f'Failover configuration "{name}" created successfully!')
        return redirect('failover_configuration')
    
    failover_configs = FailoverConfiguration.objects.filter(created_by=request.user)
    
    context = {
        'failover_configs': failover_configs,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'disaster_recovery/failover_configuration.html', context)


@owner_only
def downtime_notifications(request):
    """
    Downtime notification management - owner only
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type')
        recipients_str = request.POST.get('recipients', '')
        recipients = [r.strip() for r in recipients_str.split(',') if r.strip()]
        priority = request.POST.get('priority', 'medium')
        scheduled_at = timezone.now()
        
        notification = DowntimeNotification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            recipients=recipients,
            scheduled_at=scheduled_at,
            priority=priority,
            created_by=request.user
        )
        
        # In demo mode, mark as sent immediately
        if settings.DEMO_MODE:
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            messages.success(request, f'Demo notification "{title}" sent successfully!')
        else:
            messages.info(request, f'Notification "{title}" scheduled successfully!')
        
        return redirect('downtime_notifications')
    
    notifications = DowntimeNotification.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'disaster_recovery/downtime_notifications.html', context)


@owner_only
def backup_api_status(request):
    """
    API endpoint for backup status checks
    """
    if request.method == 'GET':
        backup_id = request.GET.get('backup_id')
        if backup_id:
            try:
                backup = BackupSnapshot.objects.get(id=backup_id, created_by=request.user)
                return JsonResponse({
                    'status': backup.status,
                    'progress': 100 if backup.status == 'completed' else 50,
                    'message': backup.error_message if backup.status == 'failed' else ''
                })
            except BackupSnapshot.DoesNotExist:
                return JsonResponse({'error': 'Backup not found'}, status=404)
        
        # Return overall backup system status
        recent_backups = BackupSnapshot.objects.filter(
            created_by=request.user,
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        )
        total_backups = recent_backups.count()
        successful_backups = recent_backups.filter(status='completed').count()
        
        return JsonResponse({
            'total_backups_week': total_backups,
            'successful_backups_week': successful_backups,
            'success_rate': (successful_backups / total_backups * 100) if total_backups > 0 else 0,
            'last_backup': recent_backups.first().created_at.isoformat() if recent_backups.exists() else None
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)