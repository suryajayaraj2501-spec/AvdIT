from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Server-rendered pages
    path('', views.notification_list_view, name='list'),
    path('mark-all-read/', views.mark_all_read_view, name='mark_all_read'),
    path('<int:pk>/read/', views.mark_read_view, name='mark_read'),

    # REST API endpoints
    path('api/', views.NotificationListAPIView.as_view(), name='api_list'),
    path('api/<int:pk>/read/', views.MarkNotificationReadAPIView.as_view(), name='api_mark_read'),
]
