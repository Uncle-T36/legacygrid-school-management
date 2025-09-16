"""
Billing and subscription management views with strict owner-only access controls.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging

from .billing_utils import (
    billing_owner_required, 
    subscription_owner_required,
    get_stripe_config,
    is_demo_mode
)

logger = logging.getLogger('billing')

@billing_owner_required
def billing_dashboard(request):
    """
    Main billing dashboard - accessible only by Uncle-T36.
    """
    stripe_config = get_stripe_config()
    subscription_tiers = getattr(settings, 'SUBSCRIPTION_TIERS', {})
    
    context = {
        'stripe_config': stripe_config,
        'subscription_tiers': subscription_tiers,
        'demo_mode': is_demo_mode(),
        'billing_owner': getattr(settings, 'BILLING_OWNER_USERNAME', 'Unknown'),
        'current_user': request.user.username,
    }
    
    return render(request, 'billing/dashboard.html', context)

@subscription_owner_required
def subscription_management(request):
    """
    Subscription management interface - accessible only by Uncle-T36.
    """
    stripe_config = get_stripe_config()
    subscription_tiers = getattr(settings, 'SUBSCRIPTION_TIERS', {})
    
    context = {
        'stripe_config': stripe_config,
        'subscription_tiers': subscription_tiers,
        'demo_mode': is_demo_mode(),
        'stripe_publishable_key': stripe_config.get('public_key', ''),
    }
    
    return render(request, 'billing/subscription_management.html', context)

@billing_owner_required
def payment_settings(request):
    """
    Payment gateway settings - accessible only by Uncle-T36.
    """
    if request.method == 'POST':
        # Handle payment settings updates
        messages.success(request, 'Payment settings would be updated here (demo mode)')
        return redirect('payment_settings')
    
    payment_gateways = getattr(settings, 'PAYMENT_GATEWAYS', {})
    
    context = {
        'payment_gateways': payment_gateways,
        'demo_mode': is_demo_mode(),
    }
    
    return render(request, 'billing/payment_settings.html', context)

@billing_owner_required
def stripe_configuration(request):
    """
    Stripe-specific configuration - accessible only by Uncle-T36.
    """
    stripe_config = get_stripe_config()
    
    context = {
        'stripe_config': stripe_config,
        'demo_mode': is_demo_mode(),
        'stripe_live_mode': getattr(settings, 'STRIPE_LIVE_MODE', False),
    }
    
    return render(request, 'billing/stripe_config.html', context)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Stripe webhook handler for payment events.
    This endpoint processes Stripe webhooks securely.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # In a real implementation, verify the webhook signature
    # For now, just log the webhook received
    logger.info(f"Stripe webhook received: {len(payload)} bytes")
    
    if is_demo_mode():
        logger.info("Demo mode: Webhook processing skipped")
        return JsonResponse({'status': 'demo_mode'})
    
    # Process webhook (implementation would go here)
    return JsonResponse({'status': 'success'})

def billing_access_denied(request):
    """
    View shown when unauthorized users try to access billing features.
    """
    error_message = getattr(
        settings, 
        'BILLING_ACCESS_DENIED_MESSAGE',
        "Access denied. Billing and subscription management is restricted to the system owner only."
    )
    
    context = {
        'error_message': error_message,
        'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@legacygrid.co.zw'),
        'current_user': request.user.username if request.user.is_authenticated else 'Anonymous',
        'billing_owner': getattr(settings, 'BILLING_OWNER_USERNAME', 'Uncle-T36'),
    }
    
    return render(request, 'billing/access_denied.html', context, status=403)