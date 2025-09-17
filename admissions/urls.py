from django.urls import path
from . import views

app_name = 'admissions'

urlpatterns = [
    path('', views.admission_list, name='admission_list'),
    path('apply/', views.online_application, name='online_application'),
    path('<int:application_id>/', views.application_detail, name='application_detail'),
]