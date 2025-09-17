from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.disaster_recovery_dashboard, name='disaster_recovery_dashboard'),
    path('backup/', views.backup_management, name='backup_management'),
    path('failover/', views.failover_configuration, name='failover_configuration'),
    path('notifications/', views.downtime_notifications, name='downtime_notifications'),
    path('api/backup-status/', views.backup_api_status, name='backup_api_status'),
]