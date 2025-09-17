from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('add/', views.staff_add, name='staff_add'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('<int:staff_id>/', views.staff_detail, name='staff_detail'),
]