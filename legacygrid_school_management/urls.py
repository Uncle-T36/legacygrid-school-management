from django.contrib import admin
from django.urls import path, include
from schools.views import home, dashboard  # Import homepage and dashboard views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schools/", include("schools.urls", namespace="schools")),
    path("billing/", include("billing.urls", namespace="billing")),
    path('dashboard/', dashboard, name='dashboard'),  # Direct dashboard route
    path('', home, name='home'),  # Homepage route
]