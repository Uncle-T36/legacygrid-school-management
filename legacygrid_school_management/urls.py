from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from schools.views import home  # Import homepage view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schools/", include("schools.urls", namespace="schools")),
    path("billing/", include("billing.urls", namespace="billing")),
    path('account/', include('account.urls', namespace='account')),  # Account app URLs
    path('', home, name='home'),  # Homepage route
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)