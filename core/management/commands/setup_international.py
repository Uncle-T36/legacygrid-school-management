from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Country, PaymentGateway, FeatureToggle

class Command(BaseCommand):
    help = 'Initialize default countries, payment gateways, and features for international use'

    def handle(self, *args, **options):
        self.stdout.write('🌍 Initializing international data...')
        
        # Create default countries
        self.create_countries()
        
        # Create default payment gateways
        self.create_payment_gateways()
        
        # Create default feature toggles
        self.create_feature_toggles()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Successfully initialized international data!')
        )

    def create_countries(self):
        """Create default countries with localization settings"""
        self.stdout.write('📍 Creating countries...')
        
        countries_data = settings.DEFAULT_COUNTRIES
        
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                code=country_data['code'],
                defaults={
                    'name': country_data['name'],
                    'currency_code': country_data['currency'],
                    'locale': country_data['locale'],
                    'is_rtl': country_data['locale'].startswith(('ar', 'ur', 'he', 'fa')),
                    'timezone': 'UTC',  # Can be enhanced per country
                    'is_active': True,
                    'supported_payment_gateways': [],  # Will be updated later
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Created country: {country.name}')
            else:
                self.stdout.write(f'  ℹ️  Country already exists: {country.name}')

    def create_payment_gateways(self):
        """Create default payment gateways"""
        self.stdout.write('💳 Creating payment gateways...')
        
        gateways_data = [
            {
                'name': 'stripe',
                'display_name': 'Stripe',
                'supports_recurring': True,
                'supports_webhooks': True,
                'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'SGD', 'JPY'],
                'countries': ['USA', 'GBR', 'CAN', 'AUS', 'DEU', 'FRA', 'ITA', 'ESP', 'NLD', 'BEL']
            },
            {
                'name': 'paystack',
                'display_name': 'Paystack',
                'supports_recurring': True,
                'supports_webhooks': True,
                'supported_currencies': ['NGN', 'USD', 'GHS', 'ZAR', 'KES'],
                'countries': ['NGA', 'GHA', 'ZAF', 'KEN']
            },
            {
                'name': 'flutterwave',
                'display_name': 'Flutterwave',
                'supports_recurring': True,
                'supports_webhooks': True,
                'supported_currencies': ['NGN', 'KES', 'GHS', 'UGX', 'TZS', 'RWF', 'ZMW', 'USD'],
                'countries': ['NGA', 'KEN', 'GHA', 'UGA', 'TZA', 'RWA', 'ZMB']
            },
            {
                'name': 'paypal',
                'display_name': 'PayPal',
                'supports_recurring': True,
                'supports_webhooks': True,
                'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'INR', 'BRL'],
                'countries': ['USA', 'GBR', 'CAN', 'AUS', 'DEU', 'FRA', 'IND', 'BRA']
            },
            {
                'name': 'mpesa',
                'display_name': 'M-Pesa',
                'supports_recurring': False,
                'supports_webhooks': True,
                'supported_currencies': ['KES'],
                'countries': ['KEN']
            },
            {
                'name': 'ecocash',
                'display_name': 'EcoCash',
                'supports_recurring': False,
                'supports_webhooks': False,
                'supported_currencies': ['USD'],
                'countries': ['ZWE']
            },
            {
                'name': 'onemoney',
                'display_name': 'OneMoney',
                'supports_recurring': False,
                'supports_webhooks': False,
                'supported_currencies': ['USD'],
                'countries': ['ZWE']
            },
            {
                'name': 'razorpay',
                'display_name': 'Razorpay',
                'supports_recurring': True,
                'supports_webhooks': True,
                'supported_currencies': ['INR'],
                'countries': ['IND']
            },
        ]
        
        for gateway_data in gateways_data:
            gateway, created = PaymentGateway.objects.get_or_create(
                name=gateway_data['name'],
                defaults={
                    'display_name': gateway_data['display_name'],
                    'is_active': False,  # Owner must activate
                    'supports_recurring': gateway_data['supports_recurring'],
                    'supports_webhooks': gateway_data['supports_webhooks'],
                    'supported_currencies': gateway_data['supported_currencies'],
                    'config': {},  # Empty config, owner must configure
                }
            )
            
            if created:
                # Add allowed countries
                countries = Country.objects.filter(code__in=gateway_data['countries'])
                gateway.allowed_countries.set(countries)
                self.stdout.write(f'  ✅ Created payment gateway: {gateway.display_name}')
            else:
                self.stdout.write(f'  ℹ️  Payment gateway already exists: {gateway.display_name}')

    def create_feature_toggles(self):
        """Create default feature toggles"""
        self.stdout.write('🎛️  Creating feature toggles...')
        
        features_data = [
            {
                'name': 'basic_dashboard',
                'description': 'Basic school management dashboard',
                'is_global': True,
                'is_enabled_globally': True,
                'requires_owner_approval': False,
            },
            {
                'name': 'premium_dashboard',
                'description': 'Advanced analytics and reporting dashboard',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
            {
                'name': 'ai_reports',
                'description': 'AI-generated student performance reports',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
            {
                'name': 'ai_chat',
                'description': 'AI-powered chat assistance',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
            {
                'name': 'multi_currency',
                'description': 'Multi-currency payment support',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
            {
                'name': 'bulk_sms',
                'description': 'Bulk SMS messaging',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
            {
                'name': 'mobile_app',
                'description': 'Mobile application access',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
            {
                'name': 'api_access',
                'description': 'Third-party API access',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
            {
                'name': 'gdpr_compliance',
                'description': 'GDPR compliance tools',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
            {
                'name': 'audit_logs',
                'description': 'Comprehensive audit logging',
                'is_global': False,
                'is_enabled_globally': False,
                'requires_owner_approval': True,
            },
        ]
        
        for feature_data in features_data:
            feature, created = FeatureToggle.objects.get_or_create(
                name=feature_data['name'],
                defaults={
                    'description': feature_data['description'],
                    'is_global': feature_data['is_global'],
                    'is_enabled_globally': feature_data['is_enabled_globally'],
                    'requires_owner_approval': feature_data['requires_owner_approval'],
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Created feature toggle: {feature.name}')
            else:
                self.stdout.write(f'  ℹ️  Feature toggle already exists: {feature.name}')