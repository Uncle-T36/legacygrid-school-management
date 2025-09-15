from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('schools:school_profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('accounts/', include('accounts_urls')),
    path("schools/", include("schools.urls")),
    path("billing/", include("billing.urls")),
]