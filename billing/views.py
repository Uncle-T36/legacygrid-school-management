from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from functools import wraps
from core.decorators import owner_only  # Use the enhanced decorator


@owner_only
def billing_dashboard(request):
    """
    Enhanced billing dashboard with international features
    """
    from core.models import Tenant, PaymentGateway
    from core.utils import get_currency_rates, format_currency
    
    # Get international statistics
    total_tenants = Tenant.objects.filter(is_active=True).count()
    active_gateways = PaymentGateway.objects.filter(is_active=True).count()
    currency_rates = get_currency_rates()
    
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'demo_mode': settings.DEMO_MODE,
        'subscription_tiers': settings.SUBSCRIPTION_TIERS,
        'total_tenants': total_tenants,
        'active_gateways': active_gateways,
        'currency_rates': currency_rates,
        'supported_currencies': settings.SUPPORTED_CURRENCIES,
        'available_features': settings.AVAILABLE_FEATURES,
    }
    return render(request, 'billing/dashboard.html', context)


@owner_only 
def subscription_management(request):
    """
    Enhanced subscription management with international features
    """
    from core.models import Tenant, Country
    from core.utils import get_available_payment_gateways
    
    # Get international data
    recent_subscriptions = Tenant.objects.filter(
        subscription_tier__in=['starter', 'professional', 'enterprise']
    ).order_by('-created_at')[:10]
    
    available_gateways = get_available_payment_gateways()
    countries_with_tenants = Country.objects.filter(
        tenant__isnull=False, is_active=True
    ).distinct()
    
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'stripe_price_id': settings.STRIPE_PRICE_ID,
        'domain': settings.DOMAIN,
        'demo_mode': settings.DEMO_MODE,
        'subscription_tiers': settings.SUBSCRIPTION_TIERS,
        'recent_subscriptions': recent_subscriptions,
        'available_gateways': available_gateways,
        'countries_with_tenants': countries_with_tenants,
        'supported_currencies': settings.SUPPORTED_CURRENCIES,
    }
    return render(request, 'billing/subscription.html', context)


@owner_only
def billing_settings(request):
    """
    Enhanced billing settings with international payment gateway management
    """
    from core.models import PaymentGateway, Country
    
    context = {
        'demo_mode': settings.DEMO_MODE,
        'supported_currencies': settings.SUPPORTED_CURRENCIES,
        'default_currency': settings.DEFAULT_CURRENCY,
        'payment_gateways': PaymentGateway.objects.all(),
        'active_countries': Country.objects.filter(is_active=True),
        'subscription_tiers': settings.SUBSCRIPTION_TIERS,
        'gateway_configs': settings.PAYMENT_GATEWAYS,
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
