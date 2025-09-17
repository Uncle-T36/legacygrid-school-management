from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.messages_inbox, name='messages_inbox'),
    path('compose/', views.compose_message, name='compose_message'),
    path('notifications/', views.notification_list, name='notification_list'),
]