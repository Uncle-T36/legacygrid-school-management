from django.urls import path
from .views import school_profile, schools_list, students_list, student_enrollment, student_grades, analytics, settings

urlpatterns = [
    path('profile/', school_profile, name='school_profile'),
    path('list/', schools_list, name='schools_list'),
    path('students/', students_list, name='students_list'),
    path('students/enrollment/', student_enrollment, name='student_enrollment'),
    path('students/grades/', student_grades, name='student_grades'),
    path('analytics/', analytics, name='analytics'),
    path('settings/', settings, name='settings'),
]