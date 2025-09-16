from django.contrib import admin
from django.urls import path, include
from schools.views import home  # Import homepage view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schools/", include("schools.urls")),
    path("billing/", include("billing.urls")),
    path('', home, name='home'),  # Homepage route
]