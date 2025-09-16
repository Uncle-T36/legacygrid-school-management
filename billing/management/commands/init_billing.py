from django.core.management.base import BaseCommand
from django.conf import settings
from billing.models import (
    Currency, SubscriptionTier, SubscriptionPrice, PaymentProvider
)


class Command(BaseCommand):
    help = 'Initialize billing system with default data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing billing system...')
        
        # Create currencies
        currencies_data = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'exchange_rate_to_usd': 1.0},
            {'code': 'ZWL', 'name': 'Zimbabwean Dollar', 'symbol': 'ZWL$', 'exchange_rate_to_usd': 0.04},
            {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R', 'exchange_rate_to_usd': 0.055},
            {'code': 'NGN', 'name': 'Nigerian Naira', 'symbol': '₦', 'exchange_rate_to_usd': 0.0013},
            {'code': 'KES', 'name': 'Kenyan Shilling', 'symbol': 'KSh', 'exchange_rate_to_usd': 0.0077},
        ]
        
        for currency_data in currencies_data:
            currency, created = Currency.objects.get_or_create(
                code=currency_data['code'],
                defaults=currency_data
            )
            if created:
                self.stdout.write(f'Created currency: {currency.code}')
        
        # Create subscription tiers
        free_tier, created = SubscriptionTier.objects.get_or_create(
            name='free',
            defaults={
                'description': 'Free plan with basic features',
                'features': ['basic_dashboard', 'basic_messaging'],
                'ai_access': False,
                'sort_order': 1,
            }
        )
        if created:
            self.stdout.write('Created free tier')
        
        premium_tier, created = SubscriptionTier.objects.get_or_create(
            name='premium',
            defaults={
                'description': 'Premium plan with all features including AI access',
                'features': ['basic_dashboard', 'premium_dashboard', 'ai_reports', 'ai_chat', 'advanced_messaging'],
                'ai_access': True,
                'sort_order': 2,
            }
        )
        if created:
            self.stdout.write('Created premium tier')
        
        # Create pricing for premium tier
        usd = Currency.objects.get(code='USD')
        zwl = Currency.objects.get(code='ZWL')
        zar = Currency.objects.get(code='ZAR')
        
        pricing_data = [
            {'tier': premium_tier, 'currency': usd, 'monthly_price': 29.99, 'annual_price': 299.99},
            {'tier': premium_tier, 'currency': zwl, 'monthly_price': 750.00, 'annual_price': 7500.00},
            {'tier': premium_tier, 'currency': zar, 'monthly_price': 549.99, 'annual_price': 5499.99},
        ]
        
        for price_data in pricing_data:
            price, created = SubscriptionPrice.objects.get_or_create(
                tier=price_data['tier'],
                currency=price_data['currency'],
                defaults={
                    'monthly_price': price_data['monthly_price'],
                    'annual_price': price_data['annual_price'],
                }
            )
            if created:
                self.stdout.write(f'Created pricing: {price}')
        
        # Create payment providers
        providers_data = [
            {
                'name': 'stripe',
                'display_name': 'Stripe',
                'supports_webhooks': True,
                'configuration': settings.PAYMENT_GATEWAYS.get('stripe', {}),
            },
            {
                'name': 'paypal',
                'display_name': 'PayPal',
                'supports_webhooks': True,
                'configuration': settings.PAYMENT_GATEWAYS.get('paypal', {}),
            },
            {
                'name': 'ecocash',
                'display_name': 'EcoCash',
                'supports_webhooks': False,
                'configuration': settings.PAYMENT_GATEWAYS.get('ecocash', {}),
            },
            {
                'name': 'onemoney',
                'display_name': 'OneMoney',
                'supports_webhooks': False,
                'configuration': settings.PAYMENT_GATEWAYS.get('onemoney', {}),
            },
        ]
        
        for provider_data in providers_data:
            provider, created = PaymentProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            if created:
                self.stdout.write(f'Created payment provider: {provider.display_name}')
                
                # Add supported currencies
                if provider.name in ['stripe', 'paypal']:
                    provider.supported_currencies.add(usd, zar)
                elif provider.name in ['ecocash', 'onemoney']:
                    provider.supported_currencies.add(zwl)
        
        self.stdout.write(self.style.SUCCESS('Billing system initialized successfully!'))