from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Server-rendered auth URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # REST API endpoints
    path('api/me/', views.CurrentUserAPIView.as_view(), name='api_me'),
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
]
