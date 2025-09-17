from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_overview, name='fee_overview'),
    path('statements/', views.fee_statements, name='fee_statements'),
    path('categories/', views.fee_categories, name='fee_categories'),
]