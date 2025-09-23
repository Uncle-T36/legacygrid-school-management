from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from .models import UserProfile
from .forms import UserProfileForm, UserUpdateForm, CustomPasswordChangeForm


@login_required
def profile_view(request):
    """User profile page with editing capabilities"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        # Check if password change is being attempted
        change_password = (
            request.POST.get('old_password') or 
            request.POST.get('new_password1') or 
            request.POST.get('new_password2')
        )
        
        password_form = None
        if change_password:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
        
        forms_valid = True
        
        # Check user form validity
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile information has been updated.')
        else:
            forms_valid = False
            
        # Check profile form validity
        if profile_form.is_valid():
            profile_form.save()
            if not user_form.is_valid():  # Only show this message if user form didn't already show one
                messages.success(request, 'Your profile information has been updated.')
        else:
            forms_valid = False
            
        # Handle password change if submitted
        if password_form:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep user logged in after password change
                messages.success(request, 'Your password has been changed successfully.')
            else:
                forms_valid = False
                
        if forms_valid:
            return redirect('account:profile')
    else:
        # GET request - initialize forms
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
        password_form = CustomPasswordChangeForm(request.user)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'profile': profile,
    }
    
    return render(request, 'account/profile.html', context)
