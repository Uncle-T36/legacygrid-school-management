from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from core.decorators import owner_only, requires_feature, api_key_required
from core.models import Tenant, Country, FeatureToggle
from core.utils import get_current_tenant, format_currency
import json

# === MOBILE APP API ENDPOINTS ===

@api_key_required
def api_school_info(request):
    """
    API endpoint for mobile app to get school information
    """
    tenant = get_current_tenant()
    if not tenant:
        return JsonResponse({'error': 'No tenant context'}, status=400)
    
    school_data = {
        'name': tenant.name,
        'country': tenant.country.name,
        'currency': tenant.country.currency_code,
        'timezone': tenant.country.timezone,
        'subscription_tier': tenant.subscription_tier,
        'features': tenant.enabled_features,
        'contact': {
            'email': tenant.contact_email,
            'phone': tenant.contact_phone,
            'address': tenant.address,
        },
        'branding': {
            'primary_color': tenant.primary_color,
            'secondary_color': tenant.secondary_color,
            'logo_url': tenant.logo.url if tenant.logo else None,
        }
    }
    
    return JsonResponse(school_data)


@api_key_required
def api_currency_rates(request):
    """
    API endpoint for current currency rates
    """
    from core.utils import get_currency_rates
    
    rates = get_currency_rates()
    supported_currencies = settings.SUPPORTED_CURRENCIES
    
    filtered_rates = {
        currency: rate for currency, rate in rates.items() 
        if currency in supported_currencies
    }
    
    return JsonResponse({
        'base_currency': 'USD',
        'rates': filtered_rates,
        'timestamp': rates.get('timestamp', None)
    })


@api_key_required
def api_features(request):
    """
    API endpoint for enabled features
    """
    tenant = get_current_tenant()
    if not tenant:
        return JsonResponse({'error': 'No tenant context'}, status=400)
    
    # Get enabled features for this tenant
    from core.models import TenantFeatureToggle
    enabled_features = TenantFeatureToggle.objects.filter(
        tenant=tenant, is_enabled=True
    ).values_list('feature__name', flat=True)
    
    # Add globally enabled features
    global_features = FeatureToggle.objects.filter(
        is_global=True, is_enabled_globally=True
    ).values_list('name', flat=True)
    
    all_features = list(set(list(enabled_features) + list(global_features)))
    
    return JsonResponse({
        'enabled_features': all_features,
        'subscription_tier': tenant.subscription_tier,
        'available_features': settings.AVAILABLE_FEATURES
    })


# === NOTIFICATION SYSTEM ===

@owner_only
def notification_templates(request):
    """
    Owner-only notification template management
    """
    from django.core.mail import send_mail
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send_test':
            template_type = request.POST.get('template_type')
            language = request.POST.get('language', 'en')
            recipient = request.POST.get('recipient')
            
            try:
                # Render the template
                subject, message = render_notification_template(template_type, language, {
                    'user_name': 'Test User',
                    'school_name': 'Test School',
                    'amount': '50.00',
                    'currency': 'USD'
                })
                
                # Send test email
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient],
                    fail_silently=False,
                )
                
                return JsonResponse({'success': True, 'message': 'Test email sent successfully'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
    
    context = {
        'languages': settings.LANGUAGES,
        'template_types': [
            'welcome', 'payment_confirmation', 'fee_reminder', 
            'grade_report', 'attendance_alert', 'system_maintenance'
        ]
    }
    
    return render(request, 'core/notification_templates.html', context)


def render_notification_template(template_type, language, context):
    """
    Render notification template in specified language
    """
    template_path = f'notifications/{language}/{template_type}.html'
    subject_path = f'notifications/{language}/{template_type}_subject.txt'
    
    try:
        # Try to render localized template
        subject = render_to_string(subject_path, context).strip()
        message = render_to_string(template_path, context)
    except:
        # Fallback to English
        template_path = f'notifications/en/{template_type}.html'
        subject_path = f'notifications/en/{template_type}_subject.txt'
        subject = render_to_string(subject_path, context).strip()
        message = render_to_string(template_path, context)
    
    return subject, message


# === MINISTRY OF EDUCATION API INTEGRATION ===

@owner_only
def ministry_integration(request):
    """
    Owner-only Ministry of Education API integration management
    """
    if request.method == 'POST':
        country_id = request.POST.get('country_id')
        api_endpoint = request.POST.get('api_endpoint')
        api_key = request.POST.get('api_key')
        is_enabled = request.POST.get('is_enabled') == 'on'
        
        country = get_object_or_404(Country, id=country_id)
        
        # Update country with ministry API settings
        if not hasattr(country, 'ministry_api_config'):
            country.ministry_api_config = {}
        
        country.ministry_api_config = {
            'endpoint': api_endpoint,
            'api_key': api_key,
            'enabled': is_enabled,
            'last_updated': timezone.now().isoformat()
        }
        country.save()
        
        messages.success(request, f'Ministry API settings updated for {country.name}')
        return redirect('core:ministry_integration')
    
    countries = Country.objects.filter(is_active=True)
    
    context = {
        'countries': countries,
        'ministry_endpoints': {
            'ZWE': 'https://api.mopse.gov.zw',
            'ZAF': 'https://api.education.gov.za',
            'NGA': 'https://api.fme.gov.ng',
            'KEN': 'https://api.education.go.ke',
            'UGA': 'https://api.education.go.ug',
            'GHA': 'https://api.moe.gov.gh',
        }
    }
    
    return render(request, 'core/ministry_integration.html', context)


# === CLOUD SETTINGS ===

@owner_only
def cloud_settings(request):
    """
    Owner-only cloud and scalability settings
    """
    if request.method == 'POST':
        cloud_config = {
            'multi_region': request.POST.get('multi_region') == 'on',
            'auto_backup': request.POST.get('auto_backup') == 'on',
            'backup_frequency': request.POST.get('backup_frequency', 'daily'),
            'disaster_recovery': request.POST.get('disaster_recovery') == 'on',
            'cdn_enabled': request.POST.get('cdn_enabled') == 'on',
            'auto_scaling': request.POST.get('auto_scaling') == 'on',
        }
        
        # Save cloud settings (in production, this would update cloud infrastructure)
        # For now, we'll store in database or cache
        
        from django.core.cache import cache
        cache.set('cloud_settings', cloud_config, timeout=None)
        
        messages.success(request, 'Cloud settings updated successfully')
        return redirect('core:cloud_settings')
    
    # Get current cloud settings
    from django.core.cache import cache
    current_settings = cache.get('cloud_settings', settings.CLOUD_SETTINGS)
    
    context = {
        'current_settings': current_settings,
        'backup_frequencies': ['hourly', 'daily', 'weekly'],
        'regions': [
            {'code': 'us-east-1', 'name': 'US East (N. Virginia)'},
            {'code': 'eu-west-1', 'name': 'Europe (Ireland)'},
            {'code': 'ap-southeast-1', 'name': 'Asia Pacific (Singapore)'},
            {'code': 'af-south-1', 'name': 'Africa (Cape Town)'},
        ]
    }
    
    return render(request, 'core/cloud_settings.html', context)


# === INTEGRATION MANAGEMENT ===

@owner_only
def integration_management(request):
    """
    Owner-only third-party integration management
    """
    if request.method == 'POST':
        integration_type = request.POST.get('integration_type')
        is_enabled = request.POST.get('is_enabled') == 'on'
        config_data = request.POST.get('config_data', '{}')
        
        try:
            config = json.loads(config_data)
            
            # Update integration settings
            from django.core.cache import cache
            integrations = cache.get('integrations', {})
            integrations[integration_type] = {
                'enabled': is_enabled,
                'config': config,
                'updated_at': timezone.now().isoformat()
            }
            cache.set('integrations', integrations, timeout=None)
            
            messages.success(request, f'{integration_type} integration updated')
        except json.JSONDecodeError:
            messages.error(request, 'Invalid JSON configuration')
        
        return redirect('core:integration_management')
    
    # Get current integrations
    from django.core.cache import cache
    integrations = cache.get('integrations', {})
    
    available_integrations = {
        'google_classroom': {
            'name': 'Google Classroom',
            'description': 'Sync assignments and grades',
            'config_fields': ['client_id', 'client_secret', 'redirect_uri']
        },
        'microsoft_teams': {
            'name': 'Microsoft Teams',
            'description': 'Virtual classroom integration',
            'config_fields': ['tenant_id', 'client_id', 'client_secret']
        },
        'zoom': {
            'name': 'Zoom',
            'description': 'Video conferencing',
            'config_fields': ['api_key', 'api_secret', 'webhook_secret']
        },
        'canvas': {
            'name': 'Canvas LMS',
            'description': 'Learning management system',
            'config_fields': ['api_url', 'access_token']
        },
        'moodle': {
            'name': 'Moodle',
            'description': 'Course management',
            'config_fields': ['api_url', 'token', 'service']
        }
    }
    
    context = {
        'integrations': integrations,
        'available_integrations': available_integrations,
    }
    
    return render(request, 'core/integration_management.html', context)