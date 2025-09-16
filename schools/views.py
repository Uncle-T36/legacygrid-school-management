from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import School
from .forms import SchoolLogoForm, SchoolForm

def home(request):
    return render(request, "home.html")

def is_owner(user):
    return user.is_superuser or user.groups.filter(name='Owner').exists()

@login_required
def school_list(request):
    """List all schools - available to all authenticated users"""
    schools = School.objects.all()
    return render(request, "schools/list.html", {"schools": schools})

@login_required
def school_create(request):
    """Create a new school - available to all authenticated users"""
    if request.method == "POST":
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            school = form.save(commit=False)
            school.owner = request.user
            school.save()
            messages.success(request, f'School "{school.name}" created successfully!')
            return redirect('school_profile')
    else:
        form = SchoolForm()
    return render(request, "schools/create.html", {"form": form})

@login_required
def school_edit(request, school_id):
    """Edit a school - only the owner or superuser can edit"""
    school = get_object_or_404(School, id=school_id)
    
    # Check if user can edit this school
    if school.owner != request.user and not request.user.is_superuser:
        messages.error(request, 'You can only edit schools you own.')
        return redirect('school_list')
    
    if request.method == "POST":
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'School "{school.name}" updated successfully!')
            return redirect('school_profile')
    else:
        form = SchoolForm(instance=school)
    return render(request, "schools/edit.html", {"form": form, "school": school})

@login_required
def school_profile(request):
    """View/edit user's own school profile"""
    try:
        school = School.objects.get(owner=request.user)
    except School.DoesNotExist:
        messages.info(request, 'You don\'t have a school yet. Create one now!')
        return redirect('school_create')
    
    if request.method == "POST":
        form = SchoolLogoForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, 'School profile updated successfully!')
            return redirect('school_profile')
    else:
        form = SchoolLogoForm(instance=school)
    return render(request, "schools/profile.html", {"form": form, "school": school})