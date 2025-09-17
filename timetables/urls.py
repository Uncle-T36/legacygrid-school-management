from django.urls import path
from . import views

app_name = 'timetables'

urlpatterns = [
    path('', views.timetable_overview, name='timetable_overview'),
    path('class/<int:class_id>/', views.class_timetable, name='class_timetable'),
]