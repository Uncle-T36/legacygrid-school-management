from django.contrib import admin
from django.urls import path, include
from schools.views import home  # Import homepage view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schools/", include("schools.urls")),
    path("billing/", include("billing.urls")),
    path("core/", include("core.urls")),  # International management
    path('i18n/', include('django.conf.urls.i18n')),  # Django i18n URLs
    path('', home, name='home'),  # Homepage route
]