from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings


def owner_required(view_func):
    """
    Decorator that checks if the user is the owner (Uncle-T36).
    Only the owner can access billing and subscription management.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.username != 'Uncle-T36':
            return render(request, 'billing/not_authorized.html', {
                'message': 'Only the project owner can access billing and subscription management.'
            })
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


@login_required
@owner_required
def billing_dashboard(request):
    """
    Main billing dashboard - only accessible by owner
    """
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'domain': settings.DOMAIN,
    }
    return render(request, 'billing/dashboard.html', context)


@login_required
@owner_required
def subscription_management(request):
    """
    Subscription management page - only accessible by owner
    """
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'stripe_price_id': settings.STRIPE_PRICE_ID,
    }
    return render(request, 'billing/subscription_management.html', context)


@login_required
@owner_required
def billing_settings(request):
    """
    Billing settings page - only accessible by owner
    """
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'domain': settings.DOMAIN,
    }
    return render(request, 'billing/billing_settings.html', context)


def not_authorized(request):
    """
    Page shown when non-owner tries to access billing functionality
    """
    return render(request, 'billing/not_authorized.html', {
        'message': 'You are not authorized to access this page. Only the project owner can manage billing and subscriptions.'
    })
