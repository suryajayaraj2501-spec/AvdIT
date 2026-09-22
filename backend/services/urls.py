from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Server-rendered templates
    path('', views.service_list_view, name='list'),
    path('create/', views.service_create_view, name='create'),
    path('<int:pk>/', views.service_detail_view, name='detail'),
    path('package/<int:package_id>/checkout/', views.service_checkout_view, name='checkout'),
]
