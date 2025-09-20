from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from .models import School
from .forms import SchoolLogoForm

def home(request):
    return render(request, "home.html")

def schools_home(request):
    """Homepage view for the schools app at /schools/"""
    return render(request, "schools/home.html")

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