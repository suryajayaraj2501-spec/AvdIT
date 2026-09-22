from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import ClientProfile
from .serializers import ClientProfileSerializer
from projects.models import Project
from proposals.models import Proposal, Contract
from teams.models import Team


# ==========================================
# Server-Rendered Views
# ==========================================

@login_required
def client_dashboard_view(request):
    profile, _ = ClientProfile.objects.get_or_create(user=request.user)

    projects = Project.objects.filter(client=profile).order_by('-created_at')
    active_projects = projects.filter(status=Project.Status.IN_PROGRESS)
    open_projects = projects.filter(status=Project.Status.OPEN)
    
    # Received proposals across client projects
    proposals = Proposal.objects.filter(project__client=profile).order_by('-created_at')[:6]
    
    # Active contracts
    contracts = Contract.objects.filter(client=profile, status=Contract.Status.ACTIVE)
    
    # Update total spent
    total_spent = Contract.objects.filter(client=profile).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    profile.total_spent = total_spent
    profile.hire_count = Contract.objects.filter(client=profile).count()
    profile.save(update_fields=['total_spent', 'hire_count'])

    return render(request, 'client/dashboard.html', {
        'profile': profile,
        'projects': projects[:5],
        'active_projects_count': active_projects.count(),
        'open_projects_count': open_projects.count(),
        'proposals': proposals,
        'contracts': contracts,
        'total_spent': total_spent,
    })


@login_required
def client_my_projects_view(request):
    profile, _ = ClientProfile.objects.get_or_create(user=request.user)
    projects = Project.objects.filter(client=profile).order_by('-created_at')
    
    return render(request, 'client/my_projects.html', {
        'profile': profile,
        'projects': projects,
    })


@login_required
def client_hire_teams_view(request):
    teams = Team.objects.filter(is_available=True).prefetch_related('members__user', 'team_skills__skill').order_by('-rating')
    return render(request, 'client/hire_teams.html', {'teams': teams})


@login_required
def client_profile_edit_view(request):
    profile, _ = ClientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.company_name = request.POST.get('company_name', profile.company_name)
        profile.industry = request.POST.get('industry', profile.industry)
        profile.company_size = request.POST.get('company_size', profile.company_size)
        profile.company_website = request.POST.get('company_website', profile.company_website)
        profile.location = request.POST.get('location', profile.location)
        profile.about_company = request.POST.get('about_company', profile.about_company)
        profile.save()

        messages.success(request, "Company profile updated successfully.")
        return redirect('clients:dashboard')

    return render(request, 'client/profile_edit.html', {'profile': profile})


# ==========================================
# REST API Endpoints
# ==========================================

class ClientDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = ClientProfile.objects.get_or_create(user=request.user)
        projects_by_status = Project.objects.filter(client=profile).values('status').annotate(count=Count('id'))
        
        status_labels = [p['status'].replace('_', ' ').title() for p in projects_by_status]
        status_data = [p['count'] for p in projects_by_status]

        if not status_labels:
            status_labels = ['Open', 'In Progress', 'Completed']
            status_data = [2, 1, 1]

        return Response({
            'total_spent': profile.total_spent,
            'hire_count': profile.hire_count,
            'status_labels': status_labels,
            'status_data': status_data
        })
