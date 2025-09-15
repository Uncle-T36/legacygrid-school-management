from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Owner-only billing dashboard
    path('', views.billing_dashboard, name='dashboard'),
    path('subscriptions/', views.subscription_management, name='subscription_management'),
    path('payments/', views.payment_management, name='payment_management'),
    path('currencies/', views.currency_management, name='currency_management'),
    path('providers/', views.payment_provider_management, name='provider_management'),
    path('templates/', views.message_templates, name='message_templates'),
    
    # Subscription actions
    path('subscription/<int:subscription_id>/action/', views.subscription_action, name='subscription_action'),
    
    # API endpoints
    path('api/payment-stats/', views.payment_stats_api, name='payment_stats_api'),
    
    # Webhook endpoints (no authentication required)
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/paypal/', views.paypal_webhook, name='paypal_webhook'),
    path('webhooks/mobile-money/', views.mobile_money_webhook, name='mobile_money_webhook'),
]