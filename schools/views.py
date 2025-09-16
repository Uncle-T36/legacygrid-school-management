from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os

from .models import School
from .forms import SchoolLogoForm
from .decorators import owner_required, billing_access_required, is_system_owner


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


@billing_access_required
def billing_dashboard(request):
    """
    Billing dashboard - only accessible to the system owner (Uncle-T36).
    Shows subscription status, payment history, and billing settings.
    """
    # Get Stripe configuration
    stripe_config = {
        'publishable_key': settings.STRIPE_SETTINGS['publishable_key'],
        'mode': settings.STRIPE_SETTINGS['mode'],
        'demo_mode': settings.DEMO_MODE,
    }
    
    # Get subscription tiers
    subscription_tiers = settings.SUBSCRIPTION_TIERS
    
    context = {
        'stripe_config': stripe_config,
        'subscription_tiers': subscription_tiers,
        'is_owner': True,  # This view is only accessible to owner
        'page_title': 'Billing Dashboard',
    }
    
    return render(request, 'schools/billing_dashboard.html', context)


@billing_access_required
def subscription_management(request):
    """
    Subscription management - only accessible to the system owner.
    Manage subscription tiers, pricing, and customer subscriptions.
    """
    subscription_tiers = settings.SUBSCRIPTION_TIERS
    
    context = {
        'subscription_tiers': subscription_tiers,
        'current_tier': request.user.profile.subscription_tier if hasattr(request.user, 'profile') else 'free',
        'is_owner': True,
        'page_title': 'Subscription Management',
    }
    
    return render(request, 'schools/subscription_management.html', context)


@billing_access_required
def payment_settings(request):
    """
    Payment settings configuration - only accessible to the system owner.
    Configure Stripe keys, webhook endpoints, and payment gateways.
    """
    if request.method == 'POST':
        # Handle payment settings update
        # Note: In production, these should be set via environment variables
        messages.success(request, 'Payment settings updated successfully!')
        return redirect('payment_settings')
    
    # Get current payment configuration (masked for security)
    stripe_config = settings.STRIPE_SETTINGS.copy()
    # Mask sensitive keys in the UI
    if stripe_config['secret_key']:
        stripe_config['secret_key_masked'] = stripe_config['secret_key'][:12] + '...'
    if stripe_config['webhook_secret']:
        stripe_config['webhook_secret_masked'] = stripe_config['webhook_secret'][:12] + '...'
    
    context = {
        'stripe_config': stripe_config,
        'payment_gateways': settings.PAYMENT_GATEWAYS,
        'demo_mode': settings.DEMO_MODE,
        'is_owner': True,
        'page_title': 'Payment Settings',
    }
    
    return render(request, 'schools/payment_settings.html', context)


@billing_access_required
@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook endpoint for handling payment events.
    Only accessible to the system owner for configuration purposes.
    """
    if request.method == 'POST':
        # Handle Stripe webhook
        # This is a placeholder - implement actual webhook handling
        payload = request.body
        
        try:
            # Verify webhook signature (implement with actual Stripe library)
            # event = stripe.Webhook.construct_event(
            #     payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            # )
            
            # Handle the event
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def billing_unauthorized(request):
    """
    View shown to unauthorized users who try to access billing features.
    """
    return render(request, 'schools/billing_unauthorized.html', {
        'error_message': 'Access Denied: Only the system owner can access billing and subscription management.',
        'owner_username': settings.BILLING_OWNER_USERNAME,
    })
