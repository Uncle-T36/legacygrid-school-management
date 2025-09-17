from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def timetable_overview(request):
    """Timetable overview"""
    return render(request, 'timetables/timetable_overview.html', {
        'title': 'Timetable Overview',
    })

@login_required
def class_timetable(request, class_id):
    """Class-specific timetable"""
    return render(request, 'timetables/class_timetable.html', {
        'title': 'Class Timetable',
        'class_id': class_id,
    })
