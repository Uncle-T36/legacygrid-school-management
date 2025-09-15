from django.core.management.base import BaseCommand
from billing.models import Currency, SubscriptionPlan, PaymentProvider, MessageTemplate


class Command(BaseCommand):
    help = 'Create initial data for billing system'

    def handle(self, *args, **options):
        self.stdout.write('Creating initial billing data...')
        
        # Create currencies
        currencies = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'rate': 1.0},
            {'code': 'ZWL', 'name': 'Zimbabwean Dollar', 'symbol': 'Z$', 'rate': 0.0028},  # Example rate
            {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R', 'rate': 0.055},
            {'code': 'NGN', 'name': 'Nigerian Naira', 'symbol': '₦', 'rate': 0.0012},
            {'code': 'KES', 'name': 'Kenyan Shilling', 'symbol': 'KSh', 'rate': 0.0077},
        ]
        
        for curr_data in currencies:
            currency, created = Currency.objects.get_or_create(
                code=curr_data['code'],
                defaults={
                    'name': curr_data['name'],
                    'symbol': curr_data['symbol'],
                    'exchange_rate_to_usd': curr_data['rate']
                }
            )
            if created:
                self.stdout.write(f'Created currency: {currency.code}')
        
        # Create subscription plans
        plans = [
            {
                'name': 'Basic School Plan',
                'plan_type': 'basic',
                'description': 'Perfect for small schools with up to 100 students',
                'price_usd': 29.99,
                'duration_days': 30,
                'max_students': 100,
                'max_teachers': 10,
                'features': ['Student Management', 'Basic Reporting', 'Email Support']
            },
            {
                'name': 'Standard School Plan',
                'plan_type': 'standard',
                'description': 'Ideal for medium schools with up to 500 students',
                'price_usd': 79.99,
                'duration_days': 30,
                'max_students': 500,
                'max_teachers': 50,
                'features': ['Student Management', 'Advanced Reporting', 'SMS Notifications', 'Priority Support']
            },
            {
                'name': 'Premium School Plan',
                'plan_type': 'premium',
                'description': 'For large schools with up to 2000 students',
                'price_usd': 199.99,
                'duration_days': 30,
                'max_students': 2000,
                'max_teachers': 200,
                'features': ['Full Features', 'Custom Reports', 'Multi-language', 'API Access', '24/7 Support']
            }
        ]
        
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'Created plan: {plan.name}')
        
        # Create payment providers
        providers = [
            {
                'name': 'Stripe',
                'provider_type': 'stripe',
                'is_zimbabwe_default': False,
                'currency_codes': ['USD', 'ZAR']
            },
            {
                'name': 'PayPal',
                'provider_type': 'paypal',
                'is_zimbabwe_default': False,
                'currency_codes': ['USD', 'ZAR']
            },
            {
                'name': 'EcoCash',
                'provider_type': 'ecocash',
                'is_zimbabwe_default': True,
                'currency_codes': ['ZWL', 'USD']
            },
            {
                'name': 'OneMoney',
                'provider_type': 'onemoney',
                'is_zimbabwe_default': True,
                'currency_codes': ['ZWL', 'USD']
            },
            {
                'name': 'Telecash',
                'provider_type': 'telecash',
                'is_zimbabwe_default': True,
                'currency_codes': ['ZWL']
            },
            {
                'name': 'MTN Mobile Money',
                'provider_type': 'mtn_mobile_money',
                'is_zimbabwe_default': False,
                'currency_codes': ['ZAR', 'NGN', 'USD']
            }
        ]
        
        for provider_data in providers:
            currency_codes = provider_data.pop('currency_codes')
            provider, created = PaymentProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            if created:
                # Add supported currencies
                currencies = Currency.objects.filter(code__in=currency_codes)
                provider.supported_currencies.set(currencies)
                self.stdout.write(f'Created provider: {provider.name}')
        
        # Create message templates
        templates = [
            # Payment Success Templates
            {
                'name': 'Payment Success - English Email',
                'message_type': 'payment_success',
                'channel': 'email',
                'language': 'en',
                'subject': 'Payment Successful - {plan_name}',
                'content': 'Your payment of {amount} {currency} has been processed successfully. Your {plan_name} subscription is now active. Transaction ID: {transaction_id}'
            },
            {
                'name': 'Payment Success - Shona SMS',
                'message_type': 'payment_success',
                'channel': 'sms',
                'language': 'sn',
                'subject': '',
                'content': 'Kubhadhara kwenyu kwe {amount} {currency} kwakaita zvakanaka. {plan_name} yangu yave kushanda. ID: {transaction_id}'
            },
            {
                'name': 'Payment Success - Ndebele SMS',
                'message_type': 'payment_success',
                'channel': 'sms',
                'language': 'nd',
                'subject': '',
                'content': 'Inkokhelo yakho ye {amount} {currency} iphumelele. {plan_name} yakho isebenza manje. ID: {transaction_id}'
            },
            
            # Payment Failed Templates
            {
                'name': 'Payment Failed - English Email',
                'message_type': 'payment_failed',
                'channel': 'email',
                'language': 'en',
                'subject': 'Payment Failed - Please Try Again',
                'content': 'Your payment of {amount} {currency} could not be processed. Reason: {reason}. Please try again or contact support.'
            },
            {
                'name': 'Payment Failed - Shona SMS',
                'message_type': 'payment_failed',
                'channel': 'sms',
                'language': 'sn',
                'subject': '',
                'content': 'Kubhadhara kwenyu kwe {amount} {currency} hakuna kuita. Chikonzero: {reason}. Edza zvakare.'
            },
            {
                'name': 'Payment Failed - Ndebele SMS',
                'message_type': 'payment_failed',
                'channel': 'sms',
                'language': 'nd',
                'subject': '',
                'content': 'Inkokhelo yakho ye {amount} {currency} ayiphumelanga. Isizatho: {reason}. Zama futhi.'
            },
            
            # Subscription Activated Templates
            {
                'name': 'Subscription Activated - English',
                'message_type': 'subscription_activated',
                'channel': 'in_app',
                'language': 'en',
                'subject': '',
                'content': 'Welcome! Your {plan_name} subscription is now active. You can now access all features until {end_date}.'
            },
            {
                'name': 'Subscription Activated - Shona',
                'message_type': 'subscription_activated',
                'channel': 'in_app',
                'language': 'sn',
                'subject': '',
                'content': 'Mauya! {plan_name} yanyu yave kushanda. Munogona kushandisa zvose kusvika {end_date}.'
            },
            {
                'name': 'Subscription Activated - Ndebele',
                'message_type': 'subscription_activated',
                'channel': 'in_app',
                'language': 'nd',
                'subject': '',
                'content': 'Siyakwamukela! {plan_name} yakho isebenza manje. Ungasebenzisa konke kuze kube ngu {end_date}.'
            }
        ]
        
        for template_data in templates:
            template, created = MessageTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'Created template: {template.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully created initial billing data!'))