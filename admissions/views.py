from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def admission_list(request):
    """List admissions/applications"""
    return render(request, 'admissions/admission_list.html', {
        'title': 'Admissions',
    })

@login_required
def online_application(request):
    """Online application form"""
    return render(request, 'admissions/online_application.html', {
        'title': 'Apply Online',
    })

@login_required
def application_detail(request, application_id):
    """Application detail view"""
    return render(request, 'admissions/application_detail.html', {
        'title': 'Application Details',
        'application_id': application_id,
    })
