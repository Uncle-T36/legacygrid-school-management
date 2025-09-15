from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class BillingSecurityTestCase(TestCase):
    """Test that billing features are restricted to owner only"""
    
    def setUp(self):
        self.client = Client()
        
        # Create owner user
        self.owner = User.objects.create_user(
            username='Uncle-T36',
            email='uncle@example.com',
            password='testpassword'
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='user@example.com',
            password='testpassword'
        )
    
    def test_owner_can_access_billing_dashboard(self):
        """Test that owner (Uncle-T36) can access billing dashboard"""
        self.client.login(username='Uncle-T36', password='testpassword')
        response = self.client.get(reverse('billing:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Billing Dashboard')
        self.assertContains(response, '[OWNER]')
    
    def test_regular_user_cannot_access_billing_dashboard(self):
        """Test that regular users cannot access billing dashboard"""
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get(reverse('billing:dashboard'))
        self.assertEqual(response.status_code, 403)
        # Check content for 403 responses
        self.assertIn(b'Access denied', response.content)
        self.assertIn(b'system owner', response.content)
    
    def test_anonymous_user_cannot_access_billing_dashboard(self):
        """Test that anonymous users cannot access billing dashboard"""
        response = self.client.get(reverse('billing:dashboard'))
        self.assertEqual(response.status_code, 401)
        # Check content for 401 responses
        self.assertIn(b'Please log in as the owner', response.content)
    
    def test_currency_management_owner_only(self):
        """Test that currency management is owner-only"""
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get(reverse('billing:currency_management'))
        self.assertEqual(response.status_code, 403)
    
    def test_payment_provider_management_owner_only(self):
        """Test that payment provider management is owner-only"""
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get(reverse('billing:provider_management'))
        self.assertEqual(response.status_code, 403)
    
    def test_subscription_management_owner_only(self):
        """Test that subscription management is owner-only"""
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get(reverse('billing:subscription_management'))
        self.assertEqual(response.status_code, 403)
