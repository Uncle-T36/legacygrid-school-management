from django.contrib import admin
from django.urls import path, include
from schools.views import home  # Import homepage view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schools/", include("schools.urls", namespace="schools")),
    path("billing/", include("billing.urls", namespace="billing")),
    # path('account/', include('account.urls', namespace='account')),  # <-- Commented out as account app doesn't exist
    path('', home, name='home'),  # Homepage route
]