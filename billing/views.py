from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import models
import json
import logging

from .models import (
    SubscriptionTier, UserSubscription, Payment, Currency,
    PaymentProvider, WebhookEvent, BillingAuditLog
)
from .decorators import owner_only_billing, demo_mode_check
from .services import SubscriptionManager, PaymentProcessor
from .currency import CurrencyConverter, ZimbabweanCurrencyHelper

logger = logging.getLogger(__name__)


@login_required
@demo_mode_check
def subscription_dashboard(request):
    """User subscription dashboard"""
    subscription = SubscriptionManager.get_user_subscription(request.user)
    
    # Get available tiers
    tiers = SubscriptionTier.objects.filter(is_active=True).order_by('sort_order')
    
    # Get recent payments
    recent_payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'subscription': subscription,
        'tiers': tiers,
        'recent_payments': recent_payments,
        'is_premium': subscription.tier.name == 'premium' if subscription else False,
    }
    
    return render(request, 'billing/dashboard.html', context)


@login_required
@demo_mode_check
def upgrade_subscription(request):
    """Subscription upgrade page"""
    if request.method == 'POST':
        tier_name = request.POST.get('tier')
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        currency_code = request.POST.get('currency', settings.DEFAULT_CURRENCY)
        payment_provider = request.POST.get('payment_provider')
        
        try:
            payment = PaymentProcessor.process_subscription_payment(
                user=request.user,
                tier_name=tier_name,
                billing_cycle=billing_cycle,
                currency_code=currency_code,
                payment_provider=payment_provider,
                payment_data=request.POST.dict()
            )
            
            if payment.status == 'completed':
                messages.success(request, f'Successfully upgraded to {tier_name}!')
                return redirect('billing:dashboard')
            else:
                messages.error(request, f'Payment failed: {payment.metadata.get("error", "Unknown error")}')
                
        except Exception as e:
            logger.error(f"Subscription upgrade failed: {e}")
            messages.error(request, f'Upgrade failed: {str(e)}')
    
    # Get available options
    tiers = SubscriptionTier.objects.filter(is_active=True).exclude(name='free')
    currencies = Currency.objects.filter(is_active=True)
    payment_providers = PaymentProvider.objects.filter(is_active=True)
    
    # Get current subscription
    current_subscription = SubscriptionManager.get_user_subscription(request.user)
    
    context = {
        'tiers': tiers,
        'currencies': currencies,
        'payment_providers': payment_providers,
        'current_subscription': current_subscription,
        'zimbabwe_currencies': ZimbabweanCurrencyHelper.get_preferred_payment_currencies(),
    }
    
    return render(request, 'billing/upgrade.html', context)


@login_required
def payment_history(request):
    """User payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'payments': page_obj.object_list,
    }
    
    return render(request, 'billing/payment_history.html', context)


@login_required
@owner_only_billing
def billing_admin(request):
    """Billing administration dashboard (owner only)"""
    # Get statistics
    total_subscriptions = UserSubscription.objects.count()
    active_subscriptions = UserSubscription.objects.filter(status='active').count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    # Recent payments
    recent_payments = Payment.objects.order_by('-created_at')[:10]
    
    # Recent subscriptions
    recent_subscriptions = UserSubscription.objects.order_by('-started_at')[:10]
    
    context = {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'recent_payments': recent_payments,
        'recent_subscriptions': recent_subscriptions,
    }
    
    return render(request, 'billing/admin_dashboard.html', context)


@login_required
@owner_only_billing
def manage_subscriptions(request):
    """Manage user subscriptions (owner only)"""
    subscriptions = UserSubscription.objects.select_related('user', 'tier').order_by('-started_at')
    
    paginator = Paginator(subscriptions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'subscriptions': page_obj.object_list,
    }
    
    return render(request, 'billing/manage_subscriptions.html', context)


@login_required
@owner_only_billing
def manage_payments(request):
    """Manage payments (owner only)"""
    payments = Payment.objects.select_related('user', 'provider', 'currency').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    paginator = Paginator(payments, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'payments': page_obj.object_list,
        'status_filter': status_filter,
        'status_choices': Payment.STATUS_CHOICES,
    }
    
    return render(request, 'billing/manage_payments.html', context)


@login_required
@owner_only_billing
def analytics_dashboard(request):
    """Billing analytics dashboard (owner only)"""
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncMonth
    
    # Monthly revenue
    monthly_revenue = Payment.objects.filter(
        status='completed',
        created_at__gte=timezone.now() - timezone.timedelta(days=365)
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('amount'),
        count=Count('id')
    ).order_by('month')
    
    # Subscription tier distribution
    tier_distribution = UserSubscription.objects.filter(
        status='active'
    ).values('tier__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Payment method distribution
    payment_method_distribution = Payment.objects.filter(
        status='completed',
        created_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).values('provider__name').annotate(
        count=Count('id'),
        revenue=Sum('amount')
    ).order_by('-revenue')
    
    context = {
        'monthly_revenue': list(monthly_revenue),
        'tier_distribution': list(tier_distribution),
        'payment_method_distribution': list(payment_method_distribution),
    }
    
    return render(request, 'billing/analytics.html', context)


@require_http_methods(["GET"])
def get_tier_pricing(request):
    """API endpoint to get tier pricing in different currencies"""
    tier_id = request.GET.get('tier_id')
    currency_code = request.GET.get('currency', settings.DEFAULT_CURRENCY)
    
    try:
        tier = SubscriptionTier.objects.get(id=tier_id, is_active=True)
        price = tier.prices.get(currency__code=currency_code, is_active=True)
        
        data = {
            'tier': tier.name,
            'currency': currency_code,
            'monthly_price': str(price.monthly_price),
            'annual_price': str(price.annual_price) if price.annual_price else None,
        }
        
        return JsonResponse(data)
        
    except (SubscriptionTier.DoesNotExist, SubscriptionTier.prices.through.DoesNotExist):
        return JsonResponse({'error': 'Pricing not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_handler(request, provider_name):
    """Generic webhook handler for payment providers"""
    logger.info(f"Received webhook from {provider_name}")
    
    try:
        provider = PaymentProvider.objects.get(name=provider_name, is_active=True)
    except PaymentProvider.DoesNotExist:
        logger.error(f"Unknown payment provider: {provider_name}")
        return HttpResponse("Unknown provider", status=400)
    
    try:
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE', '') or request.META.get('HTTP_X_PAYPAL_SIGNATURE', '')
        
        # Verify webhook if provider supports it
        if provider.supports_webhooks:
            from .gateways import PaymentGatewayFactory
            gateway = PaymentGatewayFactory.create_gateway(
                provider_name, 
                settings.PAYMENT_GATEWAYS[provider_name]
            )
            
            if not gateway.verify_webhook(payload, signature):
                logger.error(f"Webhook verification failed for {provider_name}")
                return HttpResponse("Verification failed", status=400)
        
        # Parse webhook data
        webhook_data = json.loads(payload.decode('utf-8'))
        event_type = webhook_data.get('type') or webhook_data.get('event_type')
        event_id = webhook_data.get('id') or webhook_data.get('event_id')
        
        # Create webhook event record
        webhook_event, created = WebhookEvent.objects.get_or_create(
            external_event_id=event_id,
            defaults={
                'provider': provider,
                'event_type': event_type,
                'payload': webhook_data,
            }
        )
        
        if not created:
            logger.info(f"Webhook event {event_id} already processed")
            return HttpResponse("Already processed", status=200)
        
        # Process the webhook
        success = process_webhook_event(webhook_event)
        
        if success:
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
        else:
            webhook_event.error_message = "Processing failed"
        
        webhook_event.save()
        
        return HttpResponse("OK", status=200)
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return HttpResponse("Processing failed", status=500)


def process_webhook_event(webhook_event: WebhookEvent) -> bool:
    """Process a webhook event"""
    try:
        payload = webhook_event.payload
        event_type = webhook_event.event_type
        
        if event_type in ['payment.succeeded', 'invoice.payment_succeeded']:
            # Handle successful payment
            payment_id = payload.get('data', {}).get('object', {}).get('id')
            if payment_id:
                try:
                    payment = Payment.objects.get(external_payment_id=payment_id)
                    payment.status = 'completed'
                    payment.processed_at = timezone.now()
                    payment.save()
                    
                    # Activate subscription if auto-activation is enabled
                    if payment.subscription and settings.AUTO_ACTIVATE_ON_PAYMENT:
                        SubscriptionManager.activate_subscription(payment.subscription, str(payment.id))
                    
                    logger.info(f"Payment {payment_id} marked as completed via webhook")
                    
                except Payment.DoesNotExist:
                    logger.warning(f"Payment {payment_id} not found in database")
        
        elif event_type in ['payment.failed', 'invoice.payment_failed']:
            # Handle failed payment
            payment_id = payload.get('data', {}).get('object', {}).get('id')
            if payment_id:
                try:
                    payment = Payment.objects.get(external_payment_id=payment_id)
                    payment.status = 'failed'
                    payment.save()
                    
                    logger.info(f"Payment {payment_id} marked as failed via webhook")
                    
                except Payment.DoesNotExist:
                    logger.warning(f"Payment {payment_id} not found in database")
        
        # Log the webhook processing
        BillingAuditLog.objects.create(
            action='webhook_processed',
            description=f"Processed webhook event: {event_type}",
            metadata={
                'provider': webhook_event.provider.name,
                'event_type': event_type,
                'event_id': webhook_event.external_event_id,
            }
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to process webhook event {webhook_event.external_event_id}: {e}")
        return False
