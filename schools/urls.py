from django.urls import path
from .views import (
    school_profile, 
    billing_dashboard, 
    subscription_management, 
    payment_settings,
    stripe_webhook,
    billing_unauthorized
)

urlpatterns = [
    path('profile/', school_profile, name='school_profile'),
    
    # Billing and subscription management (owner-only)
    path('billing/', billing_dashboard, name='billing_dashboard'),
    path('billing/subscriptions/', subscription_management, name='subscription_management'),
    path('billing/settings/', payment_settings, name='payment_settings'),
    path('billing/webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('billing/unauthorized/', billing_unauthorized, name='billing_unauthorized'),
]