from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def student_list(request):
    """List all students"""
    return render(request, 'students/student_list.html', {
        'title': 'Students',
        'students': [],  # Placeholder
    })

@login_required
def student_add(request):
    """Add new student"""
    return render(request, 'students/student_add.html', {
        'title': 'Add Student',
    })

@login_required
def student_detail(request, student_id):
    """Student detail view"""
    return render(request, 'students/student_detail.html', {
        'title': 'Student Details',
        'student_id': student_id,
    })

@login_required
def student_report_card(request, student_id):
    """Student report card"""
    return render(request, 'students/student_report_card.html', {
        'title': 'Report Card',
        'student_id': student_id,
    })

@login_required
def attendance_overview(request):
    """Attendance overview"""
    return render(request, 'students/attendance_overview.html', {
        'title': 'Attendance Overview',
    })

@login_required
def take_attendance(request, class_id):
    """Take attendance for class"""
    return render(request, 'students/take_attendance.html', {
        'title': 'Take Attendance',
        'class_id': class_id,
    })

@login_required
def grades_overview(request):
    """Grades overview"""
    return render(request, 'students/grades_overview.html', {
        'title': 'Grades Overview',
    })

@login_required
def enter_grades(request, assessment_id):
    """Enter grades for assessment"""
    return render(request, 'students/enter_grades.html', {
        'title': 'Enter Grades',
        'assessment_id': assessment_id,
    })