from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Server-rendered pages
    path('', views.project_list_view, name='list'),
    path('post/', views.project_create_view, name='create'),
    path('<int:pk>/', views.project_detail_view, name='detail'),
    path('<int:pk>/workspace/', views.project_workspace_view, name='workspace'),
    path('<int:project_id>/add-milestone/', views.add_milestone_view, name='add_milestone'),
    path('milestone/<int:milestone_id>/add-task/', views.add_task_view, name='add_task'),
    path('task/<int:task_id>/update-status/', views.update_task_status_view, name='update_task_status'),
]
