from django.urls import path
from .views import school_profile, school_list

app_name = 'schools'

urlpatterns = [
    path('profile/', school_profile, name='school_profile'),
    path('list/', school_list, name='list'),
]