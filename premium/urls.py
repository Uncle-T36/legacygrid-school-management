"""
URL configuration for premium app
"""
from django.urls import path
from . import views

app_name = 'premium'

urlpatterns = [
    # Premium dashboard
    path('dashboard/', views.premium_dashboard, name='dashboard'),
    
    # Analytics
    path('analytics/', views.usage_analytics, name='analytics'),
    path('activity-monitoring/', views.activity_monitoring, name='activity_monitoring'),
    
    # Backup management
    path('backups/', views.backup_management, name='backups'),
    path('backups/create/', views.create_backup, name='create_backup'),
    path('backups/<int:backup_id>/', views.backup_detail, name='backup_detail'),
    
    # Custom domains
    path('domains/', views.custom_domains, name='domains'),
    path('domains/verify/<int:domain_id>/', views.verify_domain, name='verify_domain'),
    
    # Feedback and bug reports
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/new/', views.new_feedback, name='new_feedback'),
    path('feedback/<int:feedback_id>/', views.feedback_detail, name='feedback_detail'),
    
    # Update management
    path('updates/', views.update_management, name='updates'),
    path('updates/check/', views.check_updates, name='check_updates'),
    
    # Security reviews
    path('security-reviews/', views.security_reviews, name='security_reviews'),
    path('security-reviews/<int:review_id>/', views.security_review_detail, name='security_review_detail'),
]