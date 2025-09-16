from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
from unittest.mock import patch
from billing.models import (
    Currency, SubscriptionTier, SubscriptionPrice, UserSubscription,
    PaymentProvider, Payment
)
from billing.services import SubscriptionManager, PaymentProcessor
from billing.gateways import PaymentGatewayFactory, StripeGateway
from billing.currency import CurrencyConverter
import json


class BillingModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.currency_usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            exchange_rate_to_usd=1.0
        )
        
        self.currency_zwl = Currency.objects.create(
            code='ZWL',
            name='Zimbabwean Dollar',
            symbol='ZWL$',
            exchange_rate_to_usd=0.04
        )
        
        self.free_tier = SubscriptionTier.objects.create(
            name='free',
            description='Free plan',
            features=['basic_dashboard'],
            ai_access=False
        )
        
        self.premium_tier = SubscriptionTier.objects.create(
            name='premium',
            description='Premium plan',
            features=['basic_dashboard', 'ai_access'],
            ai_access=True
        )
        
        self.premium_price = SubscriptionPrice.objects.create(
            tier=self.premium_tier,
            currency=self.currency_usd,
            monthly_price=Decimal('29.99'),
            annual_price=Decimal('299.99')
        )
    
    def test_currency_model(self):
        """Test Currency model functionality"""
        self.assertEqual(str(self.currency_usd), "USD - US Dollar")
        self.assertTrue(self.currency_usd.is_active)
    
    def test_subscription_tier_model(self):
        """Test SubscriptionTier model functionality"""
        self.assertEqual(str(self.premium_tier), "premium")
        self.assertTrue(self.premium_tier.ai_access)
        self.assertIn('ai_access', self.premium_tier.features)
    
    def test_user_subscription_model(self):
        """Test UserSubscription model functionality"""
        subscription = UserSubscription.objects.create(
            user=self.user,
            tier=self.premium_tier,
            currency=self.currency_usd,
            status='active'
        )
        
        self.assertTrue(subscription.is_active)
        self.assertTrue(subscription.has_feature('ai_access'))
        self.assertFalse(subscription.has_feature('nonexistent_feature'))


class SubscriptionManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$'
        )
        
        self.free_tier = SubscriptionTier.objects.create(
            name='free',
            description='Free plan',
            features=['basic_dashboard']
        )
        
        self.premium_tier = SubscriptionTier.objects.create(
            name='premium',
            description='Premium plan',
            features=['basic_dashboard', 'ai_access'],
            ai_access=True
        )
    
    def test_create_subscription(self):
        """Test subscription creation"""
        subscription = SubscriptionManager.create_subscription(
            user=self.user,
            tier_name='premium',
            billing_cycle='monthly',
            currency_code='USD'
        )
        
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.tier, self.premium_tier)
        self.assertEqual(subscription.billing_cycle, 'monthly')
        self.assertEqual(subscription.status, 'pending')
    
    def test_activate_subscription(self):
        """Test subscription activation"""
        subscription = SubscriptionManager.create_subscription(
            user=self.user,
            tier_name='premium',
            billing_cycle='monthly',
            currency_code='USD'
        )
        
        SubscriptionManager.activate_subscription(subscription)
        subscription.refresh_from_db()
        
        self.assertEqual(subscription.status, 'active')
    
    def test_cancel_subscription(self):
        """Test subscription cancellation"""
        subscription = SubscriptionManager.create_subscription(
            user=self.user,
            tier_name='premium',
            billing_cycle='monthly',
            currency_code='USD'
        )
        
        SubscriptionManager.cancel_subscription(subscription, reason='User request')
        subscription.refresh_from_db()
        
        self.assertEqual(subscription.status, 'cancelled')
        self.assertFalse(subscription.auto_renew)


class PaymentGatewayTestCase(TestCase):
    def test_stripe_gateway_creation(self):
        """Test Stripe gateway creation"""
        config = {
            'api_key': 'sk_test_123',
            'public_key': 'pk_test_123',
            'mode': 'test'
        }
        
        gateway = PaymentGatewayFactory.create_gateway('stripe', config)
        self.assertIsInstance(gateway, StripeGateway)
    
    def test_stripe_payment_creation(self):
        """Test Stripe payment creation in test mode"""
        config = {
            'api_key': 'sk_test_123',
            'public_key': 'pk_test_123',
            'mode': 'test'
        }
        
        gateway = StripeGateway(config)
        result = gateway.create_payment(
            amount=Decimal('29.99'),
            currency='USD',
            customer_data={'email': 'test@example.com'}
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.transaction_id)
    
    def test_supported_providers(self):
        """Test getting supported payment providers"""
        providers = PaymentGatewayFactory.get_supported_providers()
        self.assertIn('stripe', providers)
        self.assertIn('paypal', providers)
        self.assertIn('ecocash', providers)


class CurrencyConverterTestCase(TestCase):
    def setUp(self):
        Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            exchange_rate_to_usd=1.0
        )
        
        Currency.objects.create(
            code='ZWL',
            name='Zimbabwean Dollar',
            symbol='ZWL$',
            exchange_rate_to_usd=0.04
        )
    
    def test_same_currency_conversion(self):
        """Test conversion between same currencies"""
        rate = CurrencyConverter.get_exchange_rate('USD', 'USD')
        self.assertEqual(rate, Decimal('1.0'))
    
    def test_usd_to_zwl_conversion(self):
        """Test USD to ZWL conversion"""
        amount = CurrencyConverter.convert_amount(
            Decimal('100.00'), 'USD', 'ZWL'
        )
        # Should be approximately 100 / 0.04 = 2500
        self.assertGreater(amount, Decimal('2000'))
    
    def test_localized_amount(self):
        """Test getting localized amount"""
        result = CurrencyConverter.get_localized_amount(
            Decimal('100.00'), 'USD', 'ZWL'
        )
        
        self.assertEqual(result['original_amount'], Decimal('100.00'))
        self.assertEqual(result['original_currency'], 'USD')
        self.assertEqual(result['display_currency'], 'ZWL')


class BillingViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.owner_user = User.objects.create_user(
            username='Uncle-T36',
            email='owner@example.com',
            password='ownerpass123'
        )
        
        # Initialize basic billing data
        Currency.objects.create(code='USD', name='US Dollar', symbol='$')
        SubscriptionTier.objects.create(
            name='free',
            description='Free plan',
            features=['basic_dashboard']
        )
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('billing:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated_user(self):
        """Test dashboard access for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('billing:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_owner_only_billing_access(self):
        """Test that only Uncle-T36 can access billing admin"""
        # Regular user should be denied
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('billing:admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Owner should have access
        self.client.login(username='Uncle-T36', password='ownerpass123')
        response = self.client.get(reverse('billing:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_webhook_endpoint(self):
        """Test webhook endpoint"""
        PaymentProvider.objects.create(
            name='stripe',
            display_name='Stripe',
            supports_webhooks=True
        )
        
        webhook_data = {
            'type': 'payment.succeeded',
            'id': 'evt_test_123',
            'data': {'object': {'id': 'pay_test_123'}}
        }
        
        response = self.client.post(
            reverse('billing:webhook_handler', kwargs={'provider_name': 'stripe'}),
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)


class SecurityTestCase(TestCase):
    def setUp(self):
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='password123'
        )
        
        self.owner_user = User.objects.create_user(
            username='Uncle-T36',
            email='owner@example.com',
            password='password123'
        )
        
        self.client = Client()
    
    def test_billing_admin_access_control(self):
        """Test that billing admin is restricted to owner only"""
        # Test with regular user
        self.client.login(username='regular', password='password123')
        
        admin_urls = [
            'billing:admin_dashboard',
            'billing:manage_subscriptions', 
            'billing:manage_payments',
            'billing:analytics'
        ]
        
        for url_name in admin_urls:
            response = self.client.get(reverse(url_name))
            self.assertNotEqual(response.status_code, 200, 
                              f"Regular user should not access {url_name}")
        
        # Test with owner
        self.client.login(username='Uncle-T36', password='password123')
        
        for url_name in admin_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200,
                           f"Owner should be able to access {url_name}")
    
    def test_demo_mode_protection(self):
        """Test that demo mode prevents real payments"""
        self.assertTrue(settings.DEMO_MODE)
        
        # In demo mode, all payments should be marked as demo
        # This would be tested in integration with the payment processor
