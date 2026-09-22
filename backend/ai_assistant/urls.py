from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # Server-rendered pages
    path('team-builder/', views.team_builder_page_view, name='team_builder_page'),

    # REST API endpoints
    path('api/team-builder/', views.AITeamBuilderAPIView.as_view(), name='api_team_builder'),
    path('api/match-freelancers/', views.AIFreelancerMatchingAPIView.as_view(), name='api_match_freelancers'),
    path('api/generate-proposal/', views.AIProposalGeneratorAPIView.as_view(), name='api_generate_proposal'),
    path('api/improve-profile/', views.AIProfileImproverAPIView.as_view(), name='api_improve_profile'),
    path('api/decompose-project/', views.AIProjectDecomposerAPIView.as_view(), name='api_decompose_project'),
    path('api/chatbot/', views.AIChatbotAPIView.as_view(), name='api_chatbot'),
]
