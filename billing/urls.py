from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # User-facing URLs
    path('', views.subscription_dashboard, name='dashboard'),
    path('upgrade/', views.upgrade_subscription, name='upgrade'),
    path('history/', views.payment_history, name='payment_history'),
    
    # Admin URLs (owner only)
    path('admin/', views.billing_admin, name='admin_dashboard'),
    path('admin/subscriptions/', views.manage_subscriptions, name='manage_subscriptions'),
    path('admin/payments/', views.manage_payments, name='manage_payments'),
    path('admin/analytics/', views.analytics_dashboard, name='analytics'),
    
    # API endpoints
    path('api/tier-pricing/', views.get_tier_pricing, name='api_tier_pricing'),
    
    # Webhook endpoints
    path('webhooks/<str:provider_name>/', views.webhook_handler, name='webhook_handler'),
]