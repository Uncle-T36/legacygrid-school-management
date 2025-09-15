from django.urls import path
from .views import school_profile

urlpatterns = [
    path('profile/', school_profile, name='school_profile'),
]