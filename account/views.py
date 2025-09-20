from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    """Simple profile view for users to manage their account"""
    return render(request, 'account/profile.html', {
        'user': request.user
    })
