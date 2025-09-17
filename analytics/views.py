from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def analytics_dashboard(request):
    """Analytics dashboard"""
    return render(request, 'analytics/analytics_dashboard.html', {
        'title': 'Analytics Dashboard',
    })

@login_required
def analytics_reports(request):
    """Analytics reports"""
    return render(request, 'analytics/analytics_reports.html', {
        'title': 'Analytics Reports',
    })
