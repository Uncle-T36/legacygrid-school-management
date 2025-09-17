from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from core.decorators import owner_only, audit_action
from core.models import Country, Tenant, PaymentGateway, FeatureToggle, TenantFeatureToggle, AuditLog
from core.utils import get_currency_rates, convert_currency, get_available_payment_gateways
import json

@owner_only
@audit_action('view')
def international_dashboard(request):
    """
    Owner-only international management dashboard
    """
    context = {
        'total_countries': Country.objects.filter(is_active=True).count(),
        'total_tenants': Tenant.objects.filter(is_active=True).count(),
        'active_gateways': PaymentGateway.objects.filter(is_active=True).count(),
        'recent_tenants': Tenant.objects.filter(is_active=True).order_by('-created_at')[:5],
        'currency_rates': get_currency_rates(),
        'supported_currencies': settings.SUPPORTED_CURRENCIES,
    }
    return render(request, 'core/international_dashboard.html', context)


@owner_only
@audit_action('view')
def manage_countries(request):
    """
    Owner-only country management
    """
    countries = Country.objects.all().order_by('name')
    
    if request.method == 'POST':
        country_id = request.POST.get('country_id')
        action = request.POST.get('action')
        
        if action == 'toggle_active':
            country = get_object_or_404(Country, id=country_id)
            country.is_active = not country.is_active
            country.save()
            messages.success(request, f"Country {country.name} {'activated' if country.is_active else 'deactivated'}")
        
        elif action == 'update_gateways':
            country = get_object_or_404(Country, id=country_id)
            gateway_ids = request.POST.getlist('gateways')
            country.supported_payment_gateways = gateway_ids
            country.save()
            messages.success(request, f"Updated payment gateways for {country.name}")
        
        return redirect('core:manage_countries')
    
    context = {
        'countries': countries,
        'payment_gateways': PaymentGateway.objects.all(),
    }
    return render(request, 'core/manage_countries.html', context)


@owner_only
@audit_action('view')
def manage_tenants(request):
    """
    Owner-only tenant management
    """
    tenants = Tenant.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        action = request.POST.get('action')
        
        if action == 'toggle_active':
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant.is_active = not tenant.is_active
            tenant.save()
            messages.success(request, f"Tenant {tenant.name} {'activated' if tenant.is_active else 'deactivated'}")
        
        elif action == 'change_tier':
            tenant = get_object_or_404(Tenant, id=tenant_id)
            new_tier = request.POST.get('new_tier')
            tenant.subscription_tier = new_tier
            tenant.save()
            messages.success(request, f"Changed {tenant.name} subscription to {new_tier}")
        
        elif action == 'delete':
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant_name = tenant.name
            tenant.delete()
            messages.success(request, f"Deleted tenant {tenant_name}")
        
        return redirect('core:manage_tenants')
    
    context = {
        'tenants': tenants,
        'subscription_tiers': settings.SUBSCRIPTION_TIERS,
    }
    return render(request, 'core/manage_tenants.html', context)


@owner_only
@audit_action('view')
def manage_payment_gateways(request):
    """
    Owner-only payment gateway management
    """
    gateways = PaymentGateway.objects.all().order_by('display_name')
    
    if request.method == 'POST':
        gateway_id = request.POST.get('gateway_id')
        action = request.POST.get('action')
        
        if action == 'toggle_active':
            gateway = get_object_or_404(PaymentGateway, id=gateway_id)
            gateway.is_active = not gateway.is_active
            gateway.save()
            messages.success(request, f"Payment gateway {gateway.display_name} {'activated' if gateway.is_active else 'deactivated'}")
        
        elif action == 'update_config':
            gateway = get_object_or_404(PaymentGateway, id=gateway_id)
            config_data = request.POST.get('config', '{}')
            try:
                gateway.config = json.loads(config_data)
                gateway.save()
                messages.success(request, f"Updated configuration for {gateway.display_name}")
            except json.JSONDecodeError:
                messages.error(request, "Invalid JSON configuration")
        
        return redirect('core:manage_payment_gateways')
    
    context = {
        'gateways': gateways,
        'available_currencies': settings.SUPPORTED_CURRENCIES,
    }
    return render(request, 'core/manage_payment_gateways.html', context)


@owner_only
@audit_action('view')
def manage_features(request):
    """
    Owner-only feature toggle management
    """
    features = FeatureToggle.objects.all().order_by('name')
    tenants = Tenant.objects.filter(is_active=True)
    
    if request.method == 'POST':
        feature_id = request.POST.get('feature_id')
        action = request.POST.get('action')
        
        if action == 'toggle_global':
            feature = get_object_or_404(FeatureToggle, id=feature_id)
            feature.is_enabled_globally = not feature.is_enabled_globally
            feature.save()
            messages.success(request, f"Feature {feature.name} globally {'enabled' if feature.is_enabled_globally else 'disabled'}")
        
        elif action == 'toggle_tenant':
            feature = get_object_or_404(FeatureToggle, id=feature_id)
            tenant_id = request.POST.get('tenant_id')
            tenant = get_object_or_404(Tenant, id=tenant_id)
            
            tenant_feature, created = TenantFeatureToggle.objects.get_or_create(
                tenant=tenant,
                feature=feature,
                defaults={'is_enabled': True, 'approved_by': request.user, 'approved_at': timezone.now()}
            )
            
            if not created:
                tenant_feature.is_enabled = not tenant_feature.is_enabled
                tenant_feature.approved_by = request.user
                tenant_feature.approved_at = timezone.now()
                tenant_feature.save()
            
            messages.success(request, f"Feature {feature.name} {'enabled' if tenant_feature.is_enabled else 'disabled'} for {tenant.name}")
        
        return redirect('core:manage_features')
    
    # Get tenant feature toggles
    tenant_features = {}
    for tenant in tenants:
        tenant_features[tenant.id] = {}
        for feature in features:
            try:
                tf = TenantFeatureToggle.objects.get(tenant=tenant, feature=feature)
                tenant_features[tenant.id][feature.id] = tf.is_enabled
            except TenantFeatureToggle.DoesNotExist:
                tenant_features[tenant.id][feature.id] = False
    
    context = {
        'features': features,
        'tenants': tenants,
        'tenant_features': tenant_features,
        'available_features': settings.AVAILABLE_FEATURES,
    }
    return render(request, 'core/manage_features.html', context)


@owner_only
@audit_action('view')
def audit_logs(request):
    """
    Owner-only audit log viewing
    """
    logs = AuditLog.objects.all().order_by('-timestamp')
    
    # Filters
    user_filter = request.GET.get('user')
    tenant_filter = request.GET.get('tenant')
    action_filter = request.GET.get('action')
    
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    if tenant_filter:
        logs = logs.filter(tenant__name__icontains=tenant_filter)
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'action_choices': AuditLog.ACTION_CHOICES,
        'filters': {
            'user': user_filter,
            'tenant': tenant_filter,
            'action': action_filter,
        }
    }
    return render(request, 'core/audit_logs.html', context)


@owner_only
def export_data(request):
    """
    Owner-only data export functionality
    """
    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        tenant_id = request.POST.get('tenant_id')
        
        # Log the export action
        AuditLog.objects.create(
            user=request.user,
            action='export',
            resource=f'data_export_{export_type}',
            notes=f"Data export: {export_type}, Tenant: {tenant_id or 'All'}"
        )
        
        if export_type == 'tenants':
            # Export tenant data
            from django.http import HttpResponse
            import csv
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="tenants.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Name', 'Subdomain', 'Country', 'Tier', 'Active', 'Created'])
            
            tenants = Tenant.objects.all()
            if tenant_id:
                tenants = tenants.filter(id=tenant_id)
            
            for tenant in tenants:
                writer.writerow([
                    tenant.name,
                    tenant.subdomain,
                    tenant.country.name,
                    tenant.subscription_tier,
                    tenant.is_active,
                    tenant.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
        
        elif export_type == 'audit_logs':
            # Export audit logs
            from django.http import HttpResponse
            import csv
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['User', 'Tenant', 'Action', 'Resource', 'IP Address', 'Timestamp'])
            
            logs = AuditLog.objects.all().order_by('-timestamp')[:10000]  # Limit to last 10k logs
            
            for log in logs:
                writer.writerow([
                    log.user.username if log.user else 'Anonymous',
                    log.tenant.name if log.tenant else 'N/A',
                    log.action,
                    log.resource,
                    log.ip_address or 'N/A',
                    log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
    
    context = {
        'tenants': Tenant.objects.all().order_by('name'),
    }
    return render(request, 'core/export_data.html', context)


@owner_only
def currency_converter(request):
    """
    Owner-only currency conversion tool
    """
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')
        
        try:
            converted_amount = convert_currency(amount, from_currency, to_currency)
            result = {
                'success': True,
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': float(converted_amount),
            }
        except Exception as e:
            result = {
                'success': False,
                'error': str(e)
            }
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse(result)
        else:
            context = {
                'result': result,
                'currencies': settings.SUPPORTED_CURRENCIES,
            }
            return render(request, 'core/currency_converter.html', context)
    
    context = {
        'currencies': settings.SUPPORTED_CURRENCIES,
        'rates': get_currency_rates(),
    }
    return render(request, 'core/currency_converter.html', context)