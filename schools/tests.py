from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from schools.models import School


class HomeViewTest(TestCase):
    """Test cases for the home view"""
    
    def setUp(self):
        self.client = Client()
        
    def test_home_view_status_code(self):
        """Test that home view returns 200 status code"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
    def test_home_view_template(self):
        """Test that home view uses correct template"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')
        
    def test_home_view_content(self):
        """Test that home view contains expected content"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Welcome to LegacyGrid School Management!')
        self.assertContains(response, 'Features')


class SchoolProfileViewTest(TestCase):
    """Test cases for school profile view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.school = School.objects.create(
            name='Test School',
            address='123 Test Street',
            owner=self.user
        )
        
    def test_school_profile_requires_login(self):
        """Test that school profile view requires authentication"""
        response = self.client.get(reverse('school_profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_school_profile_view_authenticated(self):
        """Test school profile view for authenticated user with school"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('school_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test School')
        
    def test_school_profile_redirect_if_no_school(self):
        """Test that users without schools are redirected to create school"""
        user_without_school = User.objects.create_user(
            username='noschooluser',
            password='testpass123'
        )
        self.client.login(username='noschooluser', password='testpass123')
        response = self.client.get(reverse('school_profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to create school
        
    def test_school_profile_template(self):
        """Test that school profile view uses correct template"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('school_profile'))
        self.assertTemplateUsed(response, 'schools/profile.html')


class AuthenticationViewTest(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        self.client = Client()
        
    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        
    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        
    def test_login_view_post_valid(self):
        """Test login with valid credentials"""
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
    def test_login_view_post_invalid(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Invalid username or password')


class SchoolListViewTest(TestCase):
    """Test cases for school list view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_school_list_requires_login(self):
        """Test that school list requires authentication"""
        response = self.client.get(reverse('school_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_school_list_view_authenticated(self):
        """Test school list view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('school_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'All Schools')
        
    def test_school_list_with_schools(self):
        """Test school list view displays schools"""
        School.objects.create(name='Test School 1', owner=self.user)
        School.objects.create(name='Test School 2', owner=self.user)
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('school_list'))
        
        self.assertContains(response, 'Test School 1')
        self.assertContains(response, 'Test School 2')
        
    def test_school_list_empty(self):
        """Test school list view with no schools"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('school_list'))
        self.assertContains(response, 'No schools found')