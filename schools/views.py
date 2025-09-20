from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import School
from .forms import SchoolLogoForm

def home(request):
    return render(request, "home.html")

@login_required
def dashboard(request):
    """
    Professional dashboard view for authenticated users
    Displays user context and statistics placeholder
    """
    context = {
        'user': request.user,
        'total_users': User.objects.count(),
        'total_schools': 0,  # Default to 0 to avoid database errors
        'user_schools': 0,   # Default to 0 to avoid database errors
    }
    
    # Safely try to get school statistics
    try:
        context['total_schools'] = School.objects.count()
        if hasattr(request.user, 'school_set'):
            context['user_schools'] = School.objects.filter(owner=request.user).count()
    except Exception:
        # If the schools table doesn't exist yet, we'll use the defaults
        pass
    
    return render(request, "schools/dashboard.html", context)

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