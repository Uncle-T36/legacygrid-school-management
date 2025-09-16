from django.urls import path
from .views import school_profile
from .billing_views import (
    billing_dashboard,
    subscription_management,
    payment_settings,
    stripe_configuration,
    stripe_webhook,
    billing_access_denied
)

urlpatterns = [
    path('profile/', school_profile, name='school_profile'),
    
    # Billing and subscription management routes (owner-only access)
    path('billing/', billing_dashboard, name='billing_dashboard'),
    path('billing/subscriptions/', subscription_management, name='subscription_management'),
    path('billing/payment-settings/', payment_settings, name='payment_settings'),
    path('billing/stripe-config/', stripe_configuration, name='stripe_configuration'),
    path('billing/webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('billing/access-denied/', billing_access_denied, name='billing_access_denied'),
]