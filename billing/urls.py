from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.billing_dashboard, name='dashboard'),
    path('subscription/', views.subscription_management, name='subscription_management'),
    path('settings/', views.billing_settings, name='settings'),
    path('not-authorized/', views.not_authorized, name='not_authorized'),
]