from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from .models import School
from .forms import SchoolLogoForm

def home(request):
    return render(request, "home.html")

def is_owner(user):
    return user.is_superuser or user.groups.filter(name='Owner').exists()

@login_required
@user_passes_test(is_owner)
def school_profile(request):
    school = School.objects.get(owner=request.user)
    if request.method == "POST":
        form = SchoolLogoForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            return redirect('school_profile')
    else:
        form = SchoolLogoForm(instance=school)
    return render(request, "schools/profile.html", {"form": form, "school": school})

def schools_list(request):
    """List all schools with Bootstrap cards layout"""
    schools = School.objects.all()
    return render(request, "schools/list.html", {"schools": schools})

def students_list(request):
    """List all students with filtering and search capabilities"""
    # Placeholder view - will be implemented with actual Student model
    return render(request, "students/list.html")

def student_enrollment(request):
    """Student enrollment form"""
    # Placeholder view - will be implemented with actual enrollment logic
    return render(request, "students/enrollment.html")

def student_grades(request):
    """Student grades management"""
    # Placeholder view - will be implemented with actual grades logic
    return render(request, "students/grades.html")

def analytics(request):
    """Analytics dashboard with charts and reports"""
    # Placeholder view - will be implemented with actual analytics
    return render(request, "analytics/dashboard.html")

def settings(request):
    """System settings and configuration"""
    # Placeholder view - will be implemented with actual settings
    return render(request, "settings/dashboard.html")