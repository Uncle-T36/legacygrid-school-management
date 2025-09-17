from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student management
    path('', views.student_list, name='student_list'),
    path('add/', views.student_add, name='student_add'),
    path('<int:student_id>/', views.student_detail, name='student_detail'),
    path('<int:student_id>/report/', views.student_report_card, name='student_report_card'),
    
    # Attendance
    path('attendance/', views.attendance_overview, name='attendance_overview'),
    path('attendance/<int:class_id>/', views.take_attendance, name='take_attendance'),
    
    # Grades
    path('grades/', views.grades_overview, name='grades_overview'),
    path('grades/<int:assessment_id>/', views.enter_grades, name='enter_grades'),
]