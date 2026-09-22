from django.urls import path
from . import views

app_name = 'proposals'

urlpatterns = [
    # Server-rendered pages
    path('apply/<int:project_id>/', views.submit_proposal_view, name='submit'),
    path('my-proposals/', views.my_proposals_view, name='my_proposals'),
    path('<int:proposal_id>/accept/', views.accept_proposal_view, name='accept'),
    path('<int:proposal_id>/reject/', views.reject_proposal_view, name='reject'),
]
