from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from schools.views import home  # Import homepage view

# Helper redirect views
def redirect_to_login(request):
    return redirect('accounts:login')

def redirect_to_dashboard(request):
    return redirect('accounts:dashboard')

def redirect_to_logout(request):
    return redirect('accounts:logout')

def redirect_to_register(request):
    return redirect('accounts:register')

def redirect_to_profile(request):
    return redirect('accounts:profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schools/", include("schools.urls")),
    path("billing/", include("billing.urls")),
    path("accounts/", include("accounts.urls")),
    path('', home, name='home'),  # Homepage route
    
    # Convenience redirects
    path('login/', redirect_to_login, name='login'),
    path('logout/', redirect_to_logout, name='logout'), 
    path('register/', redirect_to_register, name='register'),
    path('dashboard/', redirect_to_dashboard, name='dashboard'),
    path('profile/', redirect_to_profile, name='profile'),
    path('settings/', redirect_to_profile, name='settings'),
]