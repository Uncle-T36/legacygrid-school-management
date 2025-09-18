from django.urls import path
from .views import school_profile, schools_home

app_name = 'schools'

urlpatterns = [
    path('', schools_home, name='home'),  # Homepage view for /schools/
    path('profile/', school_profile, name='school_profile'),
]