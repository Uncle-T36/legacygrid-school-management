from django.urls import path
from .views import school_profile, school_list, school_create, school_edit
from .auth_views import login_view, logout_view, register_view

urlpatterns = [
    path('profile/', school_profile, name='school_profile'),
    path('list/', school_list, name='school_list'),
    path('create/', school_create, name='school_create'),
    path('edit/<int:school_id>/', school_edit, name='school_edit'),
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
]