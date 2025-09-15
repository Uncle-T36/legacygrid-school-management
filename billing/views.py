from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal
import json
import logging

from .decorators import owner_required
from .models import (
    Currency, SubscriptionPlan, PaymentProvider, UserProfile, 
    Subscription, Payment, WebhookEvent, MessageTemplate, NotificationLog
)
from .services import PaymentService, CurrencyService, NotificationService

logger = logging.getLogger(__name__)


@owner_required
def billing_dashboard(request):
    """Main billing dashboard - owner only"""
    # Get summary statistics
    total_revenue = Payment.objects.filter(
        status='completed'
    ).aggregate(Sum('amount_usd'))['amount_usd__sum'] or Decimal('0')
    
    active_subscriptions = Subscription.objects.filter(status='active').count()
    pending_payments = Payment.objects.filter(status='pending').count()
    
    # Recent payments
    recent_payments = Payment.objects.select_related(
        'user', 'currency', 'provider'
    ).order_by('-created_at')[:10]
    
    # Monthly revenue chart data (last 12 months)
    monthly_revenue = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timezone.timedelta(days=30*i)
        month_end = month_start + timezone.timedelta(days=32)
        month_end = month_end.replace(day=1) - timezone.timedelta(days=1)
        
        revenue = Payment.objects.filter(
            status='completed',
            completed_at__gte=month_start,
            completed_at__lte=month_end
        ).aggregate(Sum('amount_usd'))['amount_usd__sum'] or Decimal('0')
        
        monthly_revenue.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': float(revenue)
        })
    
    monthly_revenue.reverse()
    
    context = {
        'total_revenue': total_revenue,
        'active_subscriptions': active_subscriptions,
        'pending_payments': pending_payments,
        'recent_payments': recent_payments,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'billing/dashboard.html', context)


@owner_required
def subscription_management(request):
    """Manage all subscriptions - owner only"""
    subscriptions = Subscription.objects.select_related(
        'user', 'plan'
    ).order_by('-created_at')
    
    # Filter options
    status_filter = request.GET.get('status')
    if status_filter:
        subscriptions = subscriptions.filter(status=status_filter)
    
    search = request.GET.get('search')
    if search:
        subscriptions = subscriptions.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(plan__name__icontains=search)
        )
    
    context = {
        'subscriptions': subscriptions,
        'status_choices': Subscription.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': search,
    }
    
    return render(request, 'billing/subscriptions.html', context)


@owner_required
def payment_management(request):
    """Manage all payments - owner only"""
    payments = Payment.objects.select_related(
        'user', 'currency', 'provider', 'subscription'
    ).order_by('-created_at')
    
    # Filter options
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    provider_filter = request.GET.get('provider')
    if provider_filter:
        payments = payments.filter(provider_id=provider_filter)
    
    search = request.GET.get('search')
    if search:
        payments = payments.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(provider_transaction_id__icontains=search)
        )
    
    providers = PaymentProvider.objects.filter(is_active=True)
    
    context = {
        'payments': payments,
        'status_choices': Payment.STATUS_CHOICES,
        'providers': providers,
        'current_status': status_filter,
        'current_provider': provider_filter,
        'search_query': search,
    }
    
    return render(request, 'billing/payments.html', context)


@owner_required
def currency_management(request):
    """Manage currencies and exchange rates - owner only"""
    if request.method == 'POST':
        # Update exchange rates
        currency_service = CurrencyService()
        try:
            currency_service.update_exchange_rates()
            messages.success(request, 'Exchange rates updated successfully!')
        except Exception as e:
            messages.error(request, f'Failed to update exchange rates: {str(e)}')
        
        return redirect('currency_management')
    
    currencies = Currency.objects.all().order_by('code')
    
    context = {
        'currencies': currencies,
    }
    
    return render(request, 'billing/currencies.html', context)


@owner_required
def payment_provider_management(request):
    """Manage payment providers - owner only"""
    providers = PaymentProvider.objects.prefetch_related('supported_currencies').all()
    
    context = {
        'providers': providers,
    }
    
    return render(request, 'billing/providers.html', context)


@owner_required
def message_templates(request):
    """Manage message templates - owner only"""
    templates = MessageTemplate.objects.all().order_by('message_type', 'language', 'channel')
    
    context = {
        'templates': templates,
        'message_types': MessageTemplate.MESSAGE_TYPES,
        'channels': MessageTemplate.CHANNEL_TYPES,
        'languages': UserProfile.LANGUAGE_CHOICES,
    }
    
    return render(request, 'billing/message_templates.html', context)


# Webhook handlers for automated payment processing
@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        # Process Stripe webhook
        payment_service = PaymentService()
        result = payment_service.process_stripe_webhook(payload, sig_header)
        
        if result['success']:
            return HttpResponse(status=200)
        else:
            logger.error(f"Stripe webhook error: {result['error']}")
            return HttpResponse(status=400)
            
    except Exception as e:
        logger.error(f"Stripe webhook exception: {str(e)}")
        return HttpResponse(status=500)


@csrf_exempt
@require_POST
def paypal_webhook(request):
    """Handle PayPal webhooks"""
    try:
        payload = json.loads(request.body)
        
        # Process PayPal webhook
        payment_service = PaymentService()
        result = payment_service.process_paypal_webhook(payload)
        
        if result['success']:
            return HttpResponse(status=200)
        else:
            logger.error(f"PayPal webhook error: {result['error']}")
            return HttpResponse(status=400)
            
    except Exception as e:
        logger.error(f"PayPal webhook exception: {str(e)}")
        return HttpResponse(status=500)


@csrf_exempt
@require_POST
def mobile_money_webhook(request):
    """Handle Mobile Money webhooks (EcoCash, OneMoney, etc.)"""
    try:
        payload = json.loads(request.body)
        provider_type = request.GET.get('provider')
        
        # Process Mobile Money webhook
        payment_service = PaymentService()
        result = payment_service.process_mobile_money_webhook(payload, provider_type)
        
        if result['success']:
            return HttpResponse(status=200)
        else:
            logger.error(f"Mobile Money webhook error: {result['error']}")
            return HttpResponse(status=400)
            
    except Exception as e:
        logger.error(f"Mobile Money webhook exception: {str(e)}")
        return HttpResponse(status=500)


# API endpoints for frontend interaction
@owner_required
def payment_stats_api(request):
    """API endpoint for payment statistics"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timezone.timedelta(days=days)
    
    stats = {
        'total_payments': Payment.objects.filter(created_at__gte=start_date).count(),
        'successful_payments': Payment.objects.filter(
            created_at__gte=start_date, status='completed'
        ).count(),
        'total_revenue': float(Payment.objects.filter(
            created_at__gte=start_date, status='completed'
        ).aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0),
        'by_provider': {},
        'by_currency': {},
    }
    
    # Revenue by provider
    provider_stats = Payment.objects.filter(
        created_at__gte=start_date, status='completed'
    ).values('provider__name').annotate(
        total=Sum('amount_usd'), count=Count('id')
    )
    
    for stat in provider_stats:
        stats['by_provider'][stat['provider__name']] = {
            'revenue': float(stat['total']),
            'count': stat['count']
        }
    
    # Revenue by currency
    currency_stats = Payment.objects.filter(
        created_at__gte=start_date, status='completed'
    ).values('currency__code').annotate(
        total=Sum('amount'), count=Count('id')
    )
    
    for stat in currency_stats:
        stats['by_currency'][stat['currency__code']] = {
            'revenue': float(stat['total']),
            'count': stat['count']
        }
    
    return JsonResponse(stats)


@owner_required
def subscription_action(request, subscription_id):
    """Perform actions on subscriptions (activate, suspend, cancel)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    subscription = get_object_or_404(Subscription, id=subscription_id)
    action = request.POST.get('action')
    
    if action == 'activate':
        subscription.status = 'active'
        subscription.save()
        messages.success(request, f'Subscription for {subscription.user.username} activated.')
        
    elif action == 'suspend':
        subscription.status = 'suspended'
        subscription.save()
        messages.success(request, f'Subscription for {subscription.user.username} suspended.')
        
    elif action == 'cancel':
        subscription.status = 'cancelled'
        subscription.auto_renew = False
        subscription.save()
        messages.success(request, f'Subscription for {subscription.user.username} cancelled.')
        
    else:
        messages.error(request, 'Invalid action.')
    
    return redirect('subscription_management')
