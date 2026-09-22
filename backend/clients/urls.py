from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # Server-rendered templates
    path('dashboard/', views.client_dashboard_view, name='dashboard'),
    path('my-projects/', views.client_my_projects_view, name='my_projects'),
    path('hire-teams/', views.client_hire_teams_view, name='hire_teams'),
    path('profile/edit/', views.client_profile_edit_view, name='profile_edit'),

    # REST API endpoints
    path('api/dashboard-stats/', views.ClientDashboardAPIView.as_view(), name='api_dashboard_stats'),
]
