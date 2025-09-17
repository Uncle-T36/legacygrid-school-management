from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your views here.

@login_required
def staff_list(request):
    """List all staff members"""
    return render(request, 'staff/staff_list.html', {
        'title': 'Staff Members',
        'staff_members': [],  # Placeholder
    })

@login_required 
def staff_add(request):
    """Add new staff member"""
    return render(request, 'staff/staff_add.html', {
        'title': 'Add Staff Member',
    })

@login_required
def teacher_list(request):
    """List all teachers"""
    return render(request, 'staff/teacher_list.html', {
        'title': 'Teachers',
        'teachers': [],  # Placeholder
    })

@login_required
def staff_detail(request, staff_id):
    """Staff member detail view"""
    return render(request, 'staff/staff_detail.html', {
        'title': 'Staff Details',
        'staff_id': staff_id,
    })
