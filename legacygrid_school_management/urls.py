from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('schools.urls')),  # Root URL maps to schools app (includes homepage)
    path("schools/", include("schools.urls")),
    path("billing/", include("billing.urls")),
]