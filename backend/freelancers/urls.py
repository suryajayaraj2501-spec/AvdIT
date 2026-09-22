from django.urls import path
from . import views

app_name = 'freelancers'

urlpatterns = [
    # Server-rendered pages
    path('', views.freelancer_list_view, name='list'),
    path('dashboard/', views.freelancer_dashboard_view, name='dashboard'),
    path('profile/me/', views.my_freelancer_profile_view, name='my_profile'),
    path('demos/mine/', views.my_demos_view, name='my_demos'),
    path('demos/', views.demo_showcase_view, name='demo_showcase'),
    path('demos/upload/', views.upload_demo_view, name='upload_demo'),
    path('demos/<int:pk>/', views.demo_detail_view, name='demo_detail'),
    path('demos/<int:pk>/delete/', views.delete_demo_view, name='delete_demo'),
    path('<int:pk>/', views.freelancer_detail_view, name='detail'),

    # REST API endpoints
    path('api/earnings/', views.FreelancerEarningsAPIView.as_view(), name='api_earnings'),
]
