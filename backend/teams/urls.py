from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    # Server-rendered templates
    path('', views.team_list_view, name='list'),
    path('create/', views.create_team_view, name='create'),
    path('my-teams/', views.my_teams_view, name='my_teams'),
    path('<slug:slug>/', views.team_detail_view, name='detail'),
    path('<int:team_id>/invite/', views.invite_member_view, name='invite'),
    path('invitation/<int:invite_id>/<str:action>/', views.respond_invitation_view, name='respond_invitation'),
]
