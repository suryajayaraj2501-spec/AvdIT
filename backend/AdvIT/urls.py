"""
AdvIT URL Configuration.
AI-Powered Team-Based Freelancing Marketplace.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from rest_framework import routers

from accounts.views import UserViewSet
from freelancers.views import SkillViewSet, FreelancerProfileViewSet
from teams.views import TeamViewSet
from projects.views import ProjectViewSet, MilestoneViewSet, TaskViewSet
from services.views import ServiceViewSet
from proposals.views import ProposalViewSet, ContractViewSet
from reviews.views import ReviewViewSet

# Root DRF API Router
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='api_user')
router.register(r'skills', SkillViewSet, basename='api_skill')
router.register(r'freelancers', FreelancerProfileViewSet, basename='api_freelancer')
router.register(r'teams', TeamViewSet, basename='api_team')
router.register(r'projects', ProjectViewSet, basename='api_project')
router.register(r'milestones', MilestoneViewSet, basename='api_milestone')
router.register(r'tasks', TaskViewSet, basename='api_task')
router.register(r'services', ServiceViewSet, basename='api_service')
router.register(r'proposals', ProposalViewSet, basename='api_proposal')
router.register(r'contracts', ContractViewSet, basename='api_contract')
router.register(r'reviews', ReviewViewSet, basename='api_review')


# Landing Page View
def landing_page_view(request):
    from services.models import Service
    from freelancers.models import FreelancerProfile, Skill
    from teams.models import Team
    from projects.models import Project

    featured_services = Service.objects.filter(is_active=True).select_related('freelancer__user').prefetch_related('packages')[:6]
    top_freelancers = FreelancerProfile.objects.select_related('user').prefetch_related('freelancer_skills__skill').order_by('-rating', '-total_earnings')[:6]
    featured_teams = Team.objects.filter(is_available=True).prefetch_related('members__user', 'team_skills__skill').order_by('-rating')[:4]
    recent_projects = Project.objects.filter(status=Project.Status.OPEN).select_related('client__user')[:6]
    popular_skills = Skill.objects.all()[:12]

    return render(request, 'landing/index.html', {
        'featured_services': featured_services,
        'top_freelancers': top_freelancers,
        'featured_teams': featured_teams,
        'recent_projects': recent_projects,
        'popular_skills': popular_skills,
    })


landing_patterns = ([
    path('', landing_page_view, name='index'),
], 'landing')



urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Landing Page
    path('', include(landing_patterns)),

    # Web App Template Routes
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('freelancers/', include('freelancers.urls', namespace='freelancers')),
    path('clients/', include('clients.urls', namespace='clients')),
    path('teams/', include('teams.urls', namespace='teams')),
    path('projects/', include('projects.urls', namespace='projects')),
    path('services/', include('services.urls', namespace='services')),
    path('proposals/', include('proposals.urls', namespace='proposals')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('ai/', include('ai_assistant.urls', namespace='ai_assistant')),
    path('admin-panel/', include('admin_panel.urls', namespace='admin_panel')),

    # REST Framework API Router
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
