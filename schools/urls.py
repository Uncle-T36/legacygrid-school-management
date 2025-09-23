from django.urls import path
from .views import school_profile, list

app_name = 'schools'

urlpatterns = [
    path('profile/', school_profile, name='school_profile'),
    path('list/', list, name='list'),
]