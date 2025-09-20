from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.conf import settings
from .models import School
from .forms import SchoolLogoForm

def home(request):
    context = {
        'billing_owner_username': settings.BILLING_OWNER_USERNAME,
    }
    return render(request, "home.html", context)

def is_owner(user):
    return user.is_superuser or user.groups.filter(name='Owner').exists()

@login_required
def school_list(request):
    """View to list all schools"""
    schools = School.objects.all()
    context = {
        'schools': schools,
    }
    return render(request, "schools/list.html", context)

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