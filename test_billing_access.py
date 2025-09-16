"""
Test cases for billing access controls and Stripe configuration.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from schools.billing_utils import is_billing_owner, check_billing_access


class BillingAccessControlTest(TestCase):
    def setUp(self):
        """Set up test users"""
        # Create the billing owner
        self.billing_owner = User.objects.create_user(
            username='Uncle-T36',
            email='uncle@legacygrid.co.zw',
            password='testpassword'
        )
        
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='user@example.com',
            password='testpassword'
        )
        
        self.client = Client()
    
    def test_billing_owner_access(self):
        """Test that billing owner has access to billing features"""
        self.assertTrue(is_billing_owner(self.billing_owner))
        self.assertTrue(check_billing_access(self.billing_owner))
    
    def test_regular_user_denied_access(self):
        """Test that regular users are denied billing access"""
        self.assertFalse(is_billing_owner(self.regular_user))
        self.assertFalse(check_billing_access(self.regular_user))
    
    def test_anonymous_user_denied_access(self):
        """Test that anonymous users are denied billing access"""
        from django.contrib.auth.models import AnonymousUser
        anonymous = AnonymousUser()
        self.assertFalse(is_billing_owner(anonymous))
        self.assertFalse(check_billing_access(anonymous))
    
    def test_billing_dashboard_access_control(self):
        """Test billing dashboard access control"""
        # Test with billing owner
        self.client.login(username='Uncle-T36', password='testpassword')
        response = self.client.get('/schools/billing/')
        self.assertEqual(response.status_code, 200)
        
        # Test with regular user
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get('/schools/billing/')
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Access denied", status_code=403)
    
    def test_subscription_management_access_control(self):
        """Test subscription management access control"""
        # Test with billing owner
        self.client.login(username='Uncle-T36', password='testpassword')
        response = self.client.get('/schools/billing/subscriptions/')
        self.assertEqual(response.status_code, 200)
        
        # Test with regular user
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get('/schools/billing/subscriptions/')
        self.assertEqual(response.status_code, 403)
    
    def test_payment_settings_access_control(self):
        """Test payment settings access control"""
        # Test with billing owner
        self.client.login(username='Uncle-T36', password='testpassword')
        response = self.client.get('/schools/billing/payment-settings/')
        self.assertEqual(response.status_code, 200)
        
        # Test with regular user
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get('/schools/billing/payment-settings/')
        self.assertEqual(response.status_code, 403)
    
    def test_stripe_configuration_access_control(self):
        """Test Stripe configuration access control"""
        # Test with billing owner
        self.client.login(username='Uncle-T36', password='testpassword')
        response = self.client.get('/schools/billing/stripe-config/')
        self.assertEqual(response.status_code, 200)
        
        # Test with regular user
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get('/schools/billing/stripe-config/')
        self.assertEqual(response.status_code, 403)
    
    def test_anonymous_access_denied(self):
        """Test that anonymous users get proper access denied messages"""
        response = self.client.get('/schools/billing/')
        self.assertEqual(response.status_code, 401)
        self.assertContains(response, "Please log in", status_code=401)


class StripeConfigurationTest(TestCase):
    def test_stripe_settings_exist(self):
        """Test that Stripe settings are properly configured"""
        self.assertTrue(hasattr(settings, 'STRIPE_PUBLISHABLE_KEY'))
        self.assertTrue(hasattr(settings, 'STRIPE_SECRET_KEY'))
        self.assertTrue(hasattr(settings, 'STRIPE_WEBHOOK_SECRET'))
        self.assertTrue(hasattr(settings, 'STRIPE_LIVE_MODE'))
    
    def test_payment_gateways_configuration(self):
        """Test that payment gateways are properly configured"""
        self.assertTrue(hasattr(settings, 'PAYMENT_GATEWAYS'))
        payment_gateways = getattr(settings, 'PAYMENT_GATEWAYS', {})
        self.assertIn('stripe', payment_gateways)
        
        stripe_config = payment_gateways['stripe']
        self.assertIn('api_key', stripe_config)
        self.assertIn('public_key', stripe_config)
        self.assertIn('webhook_secret', stripe_config)
    
    def test_subscription_tiers_configuration(self):
        """Test that subscription tiers are properly configured"""
        self.assertTrue(hasattr(settings, 'SUBSCRIPTION_TIERS'))
        subscription_tiers = getattr(settings, 'SUBSCRIPTION_TIERS', {})
        self.assertIn('free', subscription_tiers)
        self.assertIn('premium', subscription_tiers)
        
        # Test free tier
        free_tier = subscription_tiers['free']
        self.assertEqual(free_tier['price'], 0)
        self.assertFalse(free_tier['ai_access'])
        
        # Test premium tier
        premium_tier = subscription_tiers['premium']
        self.assertEqual(premium_tier['price'], 29.99)
        self.assertTrue(premium_tier['ai_access'])
    
    def test_billing_security_settings(self):
        """Test that billing security settings are properly configured"""
        self.assertEqual(getattr(settings, 'BILLING_OWNER_USERNAME'), 'Uncle-T36')
        self.assertTrue(getattr(settings, 'ALLOW_ONLY_OWNER_BILLING'))
        self.assertTrue(getattr(settings, 'LOG_BILLING_ACCESS_ATTEMPTS'))
        self.assertTrue(getattr(settings, 'REQUIRE_BILLING_OWNER_CONFIRMATION'))


if __name__ == '__main__':
    import django
    from django.conf import settings
    if not settings.configured:
        import os
        os.environ['DJANGO_SETTINGS_MODULE'] = 'legacygrid_school_management.settings'
        django.setup()
    
    import unittest
    unittest.main()