from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Server-rendered pages
    path('', views.inbox_view, name='inbox'),
    path('<int:pk>/', views.conversation_view, name='conversation'),
    path('start/<int:user_id>/', views.start_conversation_view, name='start_conversation'),

    # REST API endpoints
    path('conversations/<int:pk>/messages/', views.MessageListAPIView.as_view(), name='api_messages'),
    path('conversations/<int:pk>/send/', views.SendMessageAPIView.as_view(), name='api_send'),
]
