from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from functools import wraps


def owner_only(view_func):
    """
    Decorator that restricts access to only the owner (Uncle-T36).
    Redirects unauthorized users to the 'not_authorized' page.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.username == settings.BILLING_OWNER_USERNAME:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('not_authorized')
    return _wrapped_view


@owner_only
def billing_dashboard(request):
    """
    Billing dashboard - only accessible to Uncle-T36
    """
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'demo_mode': settings.DEMO_MODE,
        'subscription_tiers': settings.SUBSCRIPTION_TIERS,
    }
    return render(request, 'billing/dashboard.html', context)


@owner_only 
def subscription_management(request):
    """
    Subscription management - only accessible to Uncle-T36
    """
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'stripe_price_id': settings.STRIPE_PRICE_ID,
        'domain': settings.DOMAIN,
        'demo_mode': settings.DEMO_MODE,
    }
    return render(request, 'billing/subscription.html', context)


@owner_only
def billing_settings(request):
    """
    Billing settings - only accessible to Uncle-T36
    """
    context = {
        'demo_mode': settings.DEMO_MODE,
        'supported_currencies': settings.SUPPORTED_CURRENCIES,
        'default_currency': settings.DEFAULT_CURRENCY,
    }
    return render(request, 'billing/settings.html', context)


def not_authorized(request):
    """
    Not authorized page for users who are not the owner
    """
    context = {
        'owner_username': settings.BILLING_OWNER_USERNAME,
        'support_email': settings.SUPPORT_EMAIL,
    }
    return render(request, 'billing/not_authorized.html', context)
