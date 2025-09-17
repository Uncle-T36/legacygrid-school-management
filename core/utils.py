import requests
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
import pytz
from .models import Country, PaymentGateway
from .middleware import get_current_tenant

def get_currency_rates(base_currency='USD'):
    """
    Fetch current currency exchange rates.
    Returns a dictionary of currency rates.
    """
    try:
        url = settings.CURRENCY_CONVERSION_API_URL
        if settings.CURRENCY_CONVERSION_API_KEY:
            url += f"?access_key={settings.CURRENCY_CONVERSION_API_KEY}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'rates' in data:
            return data['rates']
        else:
            # Fallback to default rates
            return get_default_currency_rates()
    
    except Exception as e:
        # Log error and return default rates
        print(f"Currency API error: {e}")
        return get_default_currency_rates()


def get_default_currency_rates():
    """
    Fallback currency rates when API is unavailable.
    These should be updated regularly.
    """
    return {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.73,
        'ZAR': 18.50,
        'NGN': 460.0,
        'KES': 110.0,
        'GHS': 6.0,
        'UGX': 3700.0,
        'TZS': 2300.0,
        'ZWL': 322.0,
        'BWP': 11.5,
        'INR': 74.0,
        'PKR': 170.0,
        'BDT': 85.0,
        'LKR': 200.0,
        'CNY': 6.5,
        'JPY': 110.0,
        'AUD': 1.35,
        'CAD': 1.25,
        'BRL': 5.2,
        'ARS': 98.0,
        'EGP': 15.7,
        'MAD': 9.0,
        'ETB': 44.0,
        'RWF': 1000.0,
        'XAF': 550.0,
        'XOF': 550.0,
    }


def convert_currency(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another.
    """
    if from_currency == to_currency:
        return Decimal(str(amount))
    
    rates = get_currency_rates()
    
    if from_currency not in rates or to_currency not in rates:
        raise ValueError(f"Currency conversion not available for {from_currency} to {to_currency}")
    
    # Convert to USD first, then to target currency
    usd_amount = Decimal(str(amount)) / Decimal(str(rates[from_currency]))
    target_amount = usd_amount * Decimal(str(rates[to_currency]))
    
    return target_amount.quantize(Decimal('0.01'))


def get_tenant_currency():
    """
    Get the preferred currency for the current tenant.
    """
    tenant = get_current_tenant()
    if tenant and tenant.country:
        return tenant.country.currency_code
    return settings.DEFAULT_CURRENCY


def format_currency(amount, currency=None):
    """
    Format amount as currency string based on locale.
    """
    if currency is None:
        currency = get_tenant_currency()
    
    # Currency symbol mapping
    currency_symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'ZAR': 'R', 'NGN': '₦',
        'KES': 'KSh', 'GHS': '₵', 'UGX': 'USh', 'TZS': 'TSh',
        'ZWL': 'Z$', 'BWP': 'P', 'INR': '₹', 'PKR': 'Rs',
        'BDT': '৳', 'LKR': 'Rs', 'CNY': '¥', 'JPY': '¥',
        'AUD': 'A$', 'CAD': 'C$', 'BRL': 'R$', 'ARS': '$',
        'EGP': '£', 'MAD': 'MAD', 'ETB': 'Br', 'RWF': 'FRw',
        'XAF': 'FCFA', 'XOF': 'CFA',
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    # Format based on locale
    tenant = get_current_tenant()
    if tenant and tenant.country:
        locale = tenant.country.locale
        if locale.startswith('en'):
            return f"{symbol}{amount:,.2f}"
        elif locale.startswith('fr'):
            return f"{amount:,.2f} {symbol}".replace(',', ' ').replace('.', ',')
        elif locale.startswith('ar'):
            return f"{symbol} {amount:,.2f}"
    
    return f"{symbol}{amount:,.2f}"


def get_available_payment_gateways(country_code=None):
    """
    Get available payment gateways for a specific country.
    """
    if not country_code:
        tenant = get_current_tenant()
        if tenant and tenant.country:
            country_code = tenant.country.code
    
    if not country_code:
        return PaymentGateway.objects.filter(is_active=True)
    
    return PaymentGateway.objects.filter(
        is_active=True,
        allowed_countries__code=country_code
    ).distinct()


def detect_user_country(request):
    """
    Detect user's country from IP address or other means.
    This is a basic implementation - can be enhanced with GeoIP.
    """
    # Try to get country from CloudFlare header
    cf_country = request.META.get('HTTP_CF_IPCOUNTRY')
    if cf_country and cf_country != 'XX':
        return cf_country
    
    # Try to get from other headers
    country_header = request.META.get('HTTP_X_COUNTRY_CODE')
    if country_header:
        return country_header
    
    # Fallback based on Accept-Language header
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    if 'en-US' in accept_language:
        return 'USA'
    elif 'en-GB' in accept_language:
        return 'GBR'
    elif 'fr' in accept_language:
        return 'FRA'
    elif 'pt-BR' in accept_language:
        return 'BRA'
    elif 'ar' in accept_language:
        return 'ARE'  # Default to UAE for Arabic
    
    # Default fallback
    return 'USA'


def get_localized_datetime_format(datetime_obj, country_code=None):
    """
    Format datetime according to country/locale preferences.
    """
    if not country_code:
        tenant = get_current_tenant()
        if tenant and tenant.country:
            country_code = tenant.country.code
    
    try:
        country = Country.objects.get(code=country_code)
        date_format = country.date_format
        time_format = country.time_format
        
        # Convert to country timezone
        country_tz = pytz.timezone(country.timezone)
        localized_dt = timezone.localtime(datetime_obj, country_tz)
        
        # Format according to country preferences
        formatted_date = localized_dt.strftime(date_format)
        formatted_time = localized_dt.strftime(time_format)
        
        return f"{formatted_date} {formatted_time}"
    
    except Country.DoesNotExist:
        # Fallback to default formatting
        return datetime_obj.strftime('%Y-%m-%d %H:%M')


def get_regional_holidays(country_code, year=None):
    """
    Get regional holidays for a specific country and year.
    This is a basic implementation - can be enhanced with holiday APIs.
    """
    if year is None:
        year = datetime.now().year
    
    # Basic holiday mappings (can be expanded)
    holiday_mappings = {
        'USA': [
            {'name': 'New Year\'s Day', 'date': f'{year}-01-01'},
            {'name': 'Independence Day', 'date': f'{year}-07-04'},
            {'name': 'Christmas Day', 'date': f'{year}-12-25'},
        ],
        'ZWE': [
            {'name': 'New Year\'s Day', 'date': f'{year}-01-01'},
            {'name': 'Independence Day', 'date': f'{year}-04-18'},
            {'name': 'Christmas Day', 'date': f'{year}-12-25'},
            {'name': 'Boxing Day', 'date': f'{year}-12-26'},
        ],
        'ZAF': [
            {'name': 'New Year\'s Day', 'date': f'{year}-01-01'},
            {'name': 'Human Rights Day', 'date': f'{year}-03-21'},
            {'name': 'Freedom Day', 'date': f'{year}-04-27'},
            {'name': 'Workers\' Day', 'date': f'{year}-05-01'},
            {'name': 'Youth Day', 'date': f'{year}-06-16'},
            {'name': 'National Women\'s Day', 'date': f'{year}-08-09'},
            {'name': 'Heritage Day', 'date': f'{year}-09-24'},
            {'name': 'Day of Reconciliation', 'date': f'{year}-12-16'},
            {'name': 'Christmas Day', 'date': f'{year}-12-25'},
            {'name': 'Day of Goodwill', 'date': f'{year}-12-26'},
        ],
        'NGA': [
            {'name': 'New Year\'s Day', 'date': f'{year}-01-01'},
            {'name': 'Independence Day', 'date': f'{year}-10-01'},
            {'name': 'Christmas Day', 'date': f'{year}-12-25'},
            {'name': 'Boxing Day', 'date': f'{year}-12-26'},
        ],
        'KEN': [
            {'name': 'New Year\'s Day', 'date': f'{year}-01-01'},
            {'name': 'Madaraka Day', 'date': f'{year}-06-01'},
            {'name': 'Mashujaa Day', 'date': f'{year}-10-20'},
            {'name': 'Jamhuri Day', 'date': f'{year}-12-12'},
            {'name': 'Christmas Day', 'date': f'{year}-12-25'},
            {'name': 'Boxing Day', 'date': f'{year}-12-26'},
        ],
    }
    
    return holiday_mappings.get(country_code, [])


def get_grading_system(country_code):
    """
    Get the grading system used in a specific country.
    """
    grading_systems = {
        'USA': {
            'type': 'letter',
            'grades': ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F'],
            'scale': 'GPA (4.0)',
            'pass_grade': 'D',
        },
        'GBR': {
            'type': 'letter',
            'grades': ['A*', 'A', 'B', 'C', 'D', 'E', 'U'],
            'scale': 'GCSE/A-Level',
            'pass_grade': 'C',
        },
        'ZWE': {
            'type': 'number',
            'grades': [1, 2, 3, 4, 5, 6, 7, 'U'],
            'scale': 'O-Level/A-Level',
            'pass_grade': 5,
        },
        'ZAF': {
            'type': 'percentage',
            'grades': ['90-100%', '80-89%', '70-79%', '60-69%', '50-59%', '40-49%', '30-39%', '0-29%'],
            'scale': 'NSC',
            'pass_grade': '40%',
        },
        'NGA': {
            'type': 'letter',
            'grades': ['A1', 'B2', 'B3', 'C4', 'C5', 'C6', 'D7', 'E8', 'F9'],
            'scale': 'WAEC/NECO',
            'pass_grade': 'C6',
        },
        'KEN': {
            'type': 'letter',
            'grades': ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E'],
            'scale': 'KCSE',
            'pass_grade': 'D',
        },
        'IND': {
            'type': 'percentage',
            'grades': ['91-100%', '81-90%', '71-80%', '61-70%', '51-60%', '41-50%', '33-40%', '0-32%'],
            'scale': 'CBSE/ICSE',
            'pass_grade': '33%',
        },
        'FRA': {
            'type': 'number',
            'grades': ['20/20', '18-19/20', '16-17/20', '14-15/20', '12-13/20', '10-11/20', '8-9/20', '0-7/20'],
            'scale': 'French System',
            'pass_grade': '10/20',
        },
    }
    
    return grading_systems.get(country_code, grading_systems['USA'])  # Default to US system


def is_rtl_language(language_code):
    """
    Check if a language is right-to-left.
    """
    return language_code in settings.RTL_LANGUAGES


def get_tenant_domain_model():
    """
    Get the tenant domain model for multi-tenant support.
    """
    from .models import Tenant
    return Tenant


def validate_payment_gateway_config(gateway_name, config):
    """
    Validate payment gateway configuration.
    """
    required_fields = {
        'stripe': ['api_key', 'public_key'],
        'paystack': ['public_key', 'secret_key'],
        'flutterwave': ['public_key', 'secret_key'],
        'paypal': ['client_id', 'client_secret'],
        'mpesa': ['consumer_key', 'consumer_secret', 'business_short_code'],
        'razorpay': ['key_id', 'key_secret'],
    }
    
    required = required_fields.get(gateway_name, [])
    missing_fields = [field for field in required if not config.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required fields for {gateway_name}: {missing_fields}")
    
    return True