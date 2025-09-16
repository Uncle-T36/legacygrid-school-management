from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.conf import settings
from .models import School
from .forms import SchoolLogoForm
from .billing_utils import is_billing_owner

def is_owner(user):
    """Check if user is a school owner or billing owner"""
    return user.is_superuser or user.groups.filter(name='Owner').exists() or is_billing_owner(user)

@login_required
@user_passes_test(is_owner)
def school_profile(request):
    """School profile management - accessible to school owners and billing owner"""
    school = School.objects.get(owner=request.user)
    if request.method == "POST":
        form = SchoolLogoForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            return redirect('school_profile')
    else:
        form = SchoolLogoForm(instance=school)
    
    # Add billing access information to context
    context = {
        "form": form, 
        "school": school,
        "has_billing_access": is_billing_owner(request.user),
        "billing_owner": getattr(settings, 'BILLING_OWNER_USERNAME', 'Uncle-T36'),
    }
    
    return render(request, "schools/profile.html", context)
