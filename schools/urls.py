from django.urls import path
from .views import school_profile, homepage

urlpatterns = [
    path('', homepage, name='homepage'),
    path('profile/', school_profile, name='school_profile'),
]