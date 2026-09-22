from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard_view, name='dashboard'),
    path('users/', views.admin_users_view, name='users'),
    path('projects/', views.admin_projects_view, name='projects'),
    path('api/stats/', views.AdminStatsAPIView.as_view(), name='api_stats'),
]
