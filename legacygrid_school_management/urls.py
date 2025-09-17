from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from schools.views import home  # Import homepage view

# Helper redirect views
def redirect_to_login(request):
    return redirect('accounts:login')

def redirect_to_dashboard(request):
    return redirect('accounts:dashboard')

def redirect_to_logout(request):
    return redirect('accounts:logout')

def redirect_to_register(request):
    return redirect('accounts:register')

def redirect_to_profile(request):
    return redirect('accounts:profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schools/", include("schools.urls")),
    path("billing/", include("billing.urls")),
    path("accounts/", include("accounts.urls")),
    path("students/", include("students.urls")),
    path("staff/", include("staff.urls")),
    path("communications/", include("communications.urls")),
    path("timetables/", include("timetables.urls")),
    path("admissions/", include("admissions.urls")),
    path("fees/", include("fees.urls")),
    path("analytics/", include("analytics.urls")),
    path('', home, name='home'),  # Homepage route
    
    # Convenience redirects
    path('login/', redirect_to_login, name='login'),
    path('logout/', redirect_to_logout, name='logout'), 
    path('register/', redirect_to_register, name='register'),
    path('dashboard/', redirect_to_dashboard, name='dashboard'),
    path('profile/', redirect_to_profile, name='profile'),
    path('settings/', redirect_to_profile, name='settings'),
    
    # Additional convenience URLs for backward compatibility
    path('student_list/', lambda request: redirect('students:student_list'), name='student_list'),
    path('student_add/', lambda request: redirect('students:student_add'), name='student_add'),
    path('attendance_overview/', lambda request: redirect('students:attendance_overview'), name='attendance_overview'),
    path('grades_overview/', lambda request: redirect('students:grades_overview'), name='grades_overview'),
    path('teacher_list/', lambda request: redirect('staff:teacher_list'), name='teacher_list'),
    path('staff_list/', lambda request: redirect('staff:staff_list'), name='staff_list'),
    path('staff_add/', lambda request: redirect('staff:staff_add'), name='staff_add'),
    path('teacher_classes/', lambda request: redirect('staff:teacher_list'), name='teacher_classes'),
    path('teacher_attendance/', lambda request: redirect('students:attendance_overview'), name='teacher_attendance'),
    path('parent_children/', lambda request: redirect('students:student_list'), name='parent_children'),
    path('parent_fees/', lambda request: redirect('fees:fee_overview'), name='parent_fees'),
    path('messages_inbox/', lambda request: redirect('communications:messages_inbox'), name='messages_inbox'),
    path('notifications_all/', lambda request: redirect('communications:notification_list'), name='notifications_all'),
    path('analytics_dashboard/', lambda request: redirect('analytics:analytics_dashboard'), name='analytics_dashboard'),
    path('system_settings/', redirect_to_profile, name='system_settings'),
]