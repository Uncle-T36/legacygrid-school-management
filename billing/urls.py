from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('dashboard/', views.billing_dashboard, name='billing_dashboard'),
    path('subscription/', views.subscription_management, name='subscription_management'),
    path('settings/', views.billing_settings, name='billing_settings'),
    path('not-authorized/', views.not_authorized, name='not_authorized'),
]